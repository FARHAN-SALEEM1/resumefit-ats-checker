from app.parsers.resume_parser import parse_resume
from app.parsers.jd_parser import parse_job_description
from app.utils.file_extract import extract_text_from_docx
from tests.conftest import make_docx, STRONG_RESUME, STUDENT_RESUME, JD_PYTHON


def _parse(lines):
    return parse_resume(extract_text_from_docx(make_docx(lines)))


def test_resume_contact_and_sections():
    parsed = _parse(STRONG_RESUME)
    assert parsed["contact"]["email"] == "ahmed@email.com"
    assert parsed["contact"]["name"] == "Ahmed Raza"
    assert {"skills", "experience", "education"} <= set(parsed["sections_found"])


def test_resume_skills_extracted():
    parsed = _parse(STRONG_RESUME)
    for skill in ["python", "fastapi", "docker", "postgresql", "redis"]:
        assert skill in parsed["skills"]


def test_skill_match_respects_word_boundaries():
    # "r" and "go" must not match inside ordinary words.
    parsed = _parse(["Name Here", "", "Skills", "Reporting, Forgotten, Mongoose"])
    assert "r" not in parsed["skills"]
    assert "go" not in parsed["skills"]


def test_projects_used_when_no_experience_section():
    parsed = _parse(STUDENT_RESUME)
    assert "projects" in parsed["sections_found"]
    assert len(parsed["experience"]) >= 1
    assert any("Projects" in w for w in parsed["warnings"])


def test_jd_parsing():
    parsed = parse_job_description(JD_PYTHON)
    assert {"python", "fastapi", "django", "postgresql", "redis", "docker"} <= set(parsed["required_skills"])
    assert len(parsed["responsibilities"]) >= 3


def test_jd_without_known_skills_warns():
    parsed = parse_job_description("We want a motivated person who enjoys working with people every day.")
    assert parsed["required_skills"] == []
    assert parsed["warnings"]
