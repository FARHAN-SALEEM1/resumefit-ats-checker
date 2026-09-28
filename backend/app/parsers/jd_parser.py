"""
Job description parser — same rule-based philosophy as resume_parser.py.

JDs are pasted as plain text (per brief: "Job description input (text
paste)"), so no file extraction needed here — just structuring.
"""
import re
from app.utils.skills_data import flat_skills_set

EXPERIENCE_LEVEL_PATTERNS = [
    (r"\b(0[-–]1|entry[\s-]?level|fresh(er)?|no experience required)\b", "entry"),
    (r"\b(1[-–]3|2[-–]4|junior)\b\s*years?", "junior"),
    (r"\b(3[-–]5|4[-–]6|mid[\s-]?level)\b\s*years?", "mid"),
    (r"\b(5\+|6\+|7[-–]10|senior)\b\s*years?", "senior"),
]

# Lines that usually introduce a responsibilities/requirements list.
RESPONSIBILITY_TRIGGERS = [
    "responsibilities", "you will", "what you'll do", "duties",
    "requirements", "qualifications", "what we're looking for",
]

BULLET_LINE_RE = re.compile(r"^\s*[-•*●▪‣]\s+|^\s*\d+[.)]\s+")


def _extract_experience_level(text: str):
    text_lower = text.lower()
    for pattern, label in EXPERIENCE_LEVEL_PATTERNS:
        if re.search(pattern, text_lower):
            return label
    return None


def _extract_required_skills(text: str):
    text_lower = text.lower()
    found = []
    for skill in flat_skills_set():
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _extract_responsibilities(text: str):
    """
    Pull bullet-point lines as responsibilities. Falls back to sentences
    if the JD has no bullet formatting at all.
    """
    lines = text.split("\n")
    bullets = [
        BULLET_LINE_RE.sub("", line).strip()
        for line in lines
        if BULLET_LINE_RE.match(line) and len(line.strip()) > 3
    ]
    if bullets:
        return bullets

    # Fallback: split into sentences, keep the reasonably-sized ones.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if 15 < len(s.strip()) < 200][:10]


def parse_job_description(raw_text: str) -> dict:
    warnings = []

    required_skills = _extract_required_skills(raw_text)
    if not required_skills:
        warnings.append(
            "No skills matched our keyword list in this job description — "
            "matching against the resume may be unreliable."
        )

    experience_level = _extract_experience_level(raw_text)
    if not experience_level:
        warnings.append("Could not detect an explicit experience level requirement.")

    responsibilities = _extract_responsibilities(raw_text)
    if not responsibilities:
        warnings.append("Could not extract distinct responsibility/requirement lines.")

    return {
        "required_skills": required_skills,
        "experience_level": experience_level,
        "responsibilities": responsibilities,
        "warnings": warnings,
    }
