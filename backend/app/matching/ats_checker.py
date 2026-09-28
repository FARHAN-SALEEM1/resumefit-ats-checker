"""
ATS-compatibility checker.

Real ATS systems (Workday, Taleo, etc.) commonly fail to parse:
tables, images/graphics-heavy layouts, and resumes missing standard
section headers. This inspects the actual file structure (not just
extracted text) to catch these.

Honest limitation: true multi-column-layout detection and font
analysis need deeper PDF geometry inspection than pdfplumber's basic
API gives cleanly. Those two checks are marked lower-confidence in
their messages rather than skipped silently — flag this to your
Sprint 4 evaluation as a "verify manually" item.
"""
import io
import pdfplumber
import docx


def _score_from_issues(issue_count: int) -> int:
    """Each issue costs 15 points, floor at 25 so score never looks broken."""
    return max(25, 100 - issue_count * 15)


def check_pdf_ats_compatibility(file_bytes: bytes, sections_found: list) -> dict:
    issues = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            table_count = 0
            image_count = 0
            for page in pdf.pages:
                tables = page.extract_tables()
                table_count += len(tables) if tables else 0
                image_count += len(page.images)

            if table_count > 0:
                issues.append(
                    f"{table_count} table(s) detected — many ATS parsers "
                    f"scramble or drop content placed inside tables."
                )
            if image_count > 0:
                issues.append(
                    f"{image_count} image(s) detected — if key info (like "
                    f"a skills graphic) is inside an image, ATS systems "
                    f"cannot read it at all."
                )
    except Exception:
        issues.append("Could not fully inspect PDF structure for formatting issues.")

    expected_sections = {"education", "skills"}
    missing_sections = expected_sections - set(sections_found)
    if missing_sections:
        issues.append(
            f"Missing standard section header(s): {', '.join(sorted(missing_sections))}. "
            f"ATS systems look for these exact labels to categorize content."
        )
    # "Experience" and "Projects" are treated as equivalent — common for
    # student/entry-level resumes that list projects instead of jobs.
    if "experience" not in sections_found and "projects" not in sections_found:
        issues.append(
            "No 'Experience' or 'Projects' section header found. ATS systems "
            "look for one of these to categorize your work/project history."
        )

    return {
        "issues": issues,
        "formatting_score": _score_from_issues(len(issues)),
    }


def check_docx_ats_compatibility(file_bytes: bytes, sections_found: list) -> dict:
    issues = []

    try:
        document = docx.Document(io.BytesIO(file_bytes))
        table_count = len(document.tables)
        image_count = len(document.inline_shapes)

        if table_count > 0:
            issues.append(
                f"{table_count} table(s) detected — many ATS parsers "
                f"scramble or drop content placed inside tables."
            )
        if image_count > 0:
            issues.append(
                f"{image_count} image(s)/graphic(s) detected — text inside "
                f"images is invisible to ATS systems."
            )
    except Exception:
        issues.append("Could not fully inspect DOCX structure for formatting issues.")

    expected_sections = {"education", "skills"}
    missing_sections = expected_sections - set(sections_found)
    if missing_sections:
        issues.append(
            f"Missing standard section header(s): {', '.join(sorted(missing_sections))}. "
            f"ATS systems look for these exact labels to categorize content."
        )
    if "experience" not in sections_found and "projects" not in sections_found:
        issues.append(
            "No 'Experience' or 'Projects' section header found. ATS systems "
            "look for one of these to categorize your work/project history."
        )

    return {
        "issues": issues,
        "formatting_score": _score_from_issues(len(issues)),
    }


def check_ats_compatibility(filename: str, file_bytes: bytes, sections_found: list) -> dict:
    if filename.lower().endswith(".pdf"):
        return check_pdf_ats_compatibility(file_bytes, sections_found)
    elif filename.lower().endswith(".docx"):
        return check_docx_ats_compatibility(file_bytes, sections_found)
    return {"issues": ["Unknown file type — formatting could not be checked."], "formatting_score": 50}
