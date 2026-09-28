"""
Resume parser — rule-based (regex + heuristics), not ML, for Sprint 1.

Why rule-based for week 1: resumes have huge format variety, and a
from-scratch NER model needs labeled training data we don't have yet.
Regex + section-header detection gets us usable structured data fast
and is fully debuggable. This is a documented MVP tradeoff, not a
final architecture — Sprint 2/3 evaluation should tell us if specific
resume formats need a smarter parser.
"""
import re
from app.utils.skills_data import flat_skills_set

# Standard section headers we look for (case-insensitive).
SECTION_HEADERS = {
    "experience": [
        "work experience", "professional experience", "experience",
        "employment history", "work history",
    ],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "summary": ["summary", "objective", "profile", "about me"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(linkedin\.com/in/[A-Za-z0-9\-_/]+)")
GITHUB_RE = re.compile(r"(github\.com/[A-Za-z0-9\-_/]+)")

# A rough date-range pattern used to spot experience/education entries,
# e.g. "Jan 2022 - Present", "2019-2021", "March 2020 – June 2021"
DATE_RANGE_RE = re.compile(
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|\d{4})"
    r"\s*[-–—to]{1,4}\s*"
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|\d{4}|present|current)",
    re.IGNORECASE,
)


def _find_section_boundaries(lines):
    """Return {section_key: (start_line_idx, end_line_idx)} for detected sections."""
    boundaries = {}
    lower_lines = [l.strip().lower() for l in lines]

    hits = []  # (line_idx, section_key)
    for idx, line in enumerate(lower_lines):
        # Section headers are usually short lines (a title), not sentences.
        if len(line) > 40 or len(line) == 0:
            continue
        for key, variants in SECTION_HEADERS.items():
            for variant in variants:
                if line == variant or line.rstrip(":") == variant:
                    hits.append((idx, key))
                    break

    hits.sort()
    for i, (idx, key) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(lines)
        boundaries[key] = (idx + 1, end)  # +1 to skip the header line itself
    return boundaries


def _extract_contact(text: str, lines):
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)
    github_match = GITHUB_RE.search(text)

    # Heuristic: name is usually the first non-empty line, if it doesn't
    # look like an email/phone/section header itself.
    name = None
    for line in lines[:5]:
        stripped = line.strip()
        if not stripped:
            continue
        if EMAIL_RE.search(stripped) or PHONE_RE.search(stripped):
            continue
        if len(stripped.split()) <= 5 and len(stripped) < 50:
            name = stripped
            break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
    }


def _extract_skills(text: str):
    text_lower = text.lower()
    found = []
    for skill in flat_skills_set():
        # word-boundary-ish match so "r" doesn't match inside "for"
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _extract_block_entries(lines, start, end):
    """
    Generic splitter for experience/education blocks: groups lines into
    entries wherever a date range is detected (assumed to mark a new entry),
    and keeps subsequent lines as bullets/details for that entry.
    """
    entries = []
    current = None
    for line in lines[start:end]:
        stripped = line.strip()
        if not stripped:
            continue
        if DATE_RANGE_RE.search(stripped):
            if current:
                entries.append(current)
            current = {"header": stripped, "bullets": []}
        else:
            if current is None:
                current = {"header": stripped, "bullets": []}
            else:
                current["bullets"].append(stripped)
    if current:
        entries.append(current)
    return entries


def parse_resume(raw_text: str) -> dict:
    lines = raw_text.split("\n")
    boundaries = _find_section_boundaries(lines)
    warnings = []

    contact = _extract_contact(raw_text, lines)
    if not contact["email"]:
        warnings.append("No email address detected — please verify manually.")
    if not contact["name"]:
        warnings.append("Could not confidently detect candidate name.")

    skills = _extract_skills(raw_text)
    if len(skills) == 0:
        warnings.append(
            "No skills matched our keyword list — either the resume has no "
            "'Skills' section, or it uses terms not yet in our skills database."
        )

    experience = []
    if "experience" in boundaries:
        start, end = boundaries["experience"]
        experience = _extract_block_entries(lines, start, end)
    elif "projects" in boundaries:
        # Common for students/entry-level candidates with no formal work
        # history: Projects section functions as their experience section.
        start, end = boundaries["projects"]
        experience = _extract_block_entries(lines, start, end)
        warnings.append(
            "No 'Experience' section found — using 'Projects' as an "
            "experience-equivalent (normal for student/entry-level resumes)."
        )
    else:
        warnings.append("No 'Experience' or 'Projects' section header detected.")

    education = []
    if "education" in boundaries:
        start, end = boundaries["education"]
        education = _extract_block_entries(lines, start, end)
    else:
        warnings.append("No 'Education' section header detected.")

    return {
        "contact": contact,
        "skills": skills,
        "experience": experience,
        "education": education,
        "sections_found": list(boundaries.keys()),
        "warnings": warnings,
    }
