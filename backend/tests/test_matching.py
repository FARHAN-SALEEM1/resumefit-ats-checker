from app.matching.gap_analysis import analyze_skill_gap
from app.matching.scorer import (
    estimate_level_from_years, score_experience_match, compute_final_score,
)
from app.matching.ats_checker import check_ats_compatibility
from tests.conftest import make_docx


def test_gap_analysis_sets():
    gap = analyze_skill_gap(["python", "git"], ["python", "docker", "git", "aws"])
    assert gap["matched_skills"] == ["git", "python"]
    assert gap["missing_skills"] == ["aws", "docker"]
    assert gap["match_percentage"] == 50.0


def test_gap_analysis_no_requirements_gives_none():
    assert analyze_skill_gap(["python"], [])["match_percentage"] is None


def test_level_buckets():
    assert estimate_level_from_years(0) == "entry"
    assert estimate_level_from_years(2) == "junior"
    assert estimate_level_from_years(4) == "mid"
    assert estimate_level_from_years(8) == "senior"


def test_experience_match_exact_and_neutral():
    entries = [{"header": "Jan 2022 - Jan 2024 Dev", "bullets": []}]
    assert score_experience_match(entries, "junior")["score"] == 100
    assert score_experience_match(entries, None)["score"] == 70  # nothing to compare


def test_final_score_weights():
    out = compute_final_score(80, 100, 50)
    assert out["overall_score"] == round(80 * 0.5 + 100 * 0.3 + 50 * 0.2, 1)


def test_final_score_redistributes_when_no_keywords():
    out = compute_final_score(None, 100, 50)
    assert out["weights_used"]["keyword_match"] == 0
    assert out["overall_score"] == round(100 * 0.6 + 50 * 0.4, 1)


def test_ats_flags_tables():
    data = make_docx(["Name", "Skills", "Education", "Experience"], table=True)
    result = check_ats_compatibility("cv.docx", data, ["skills", "education", "experience"])
    assert any("table" in issue.lower() for issue in result["issues"])
    assert result["formatting_score"] < 100


def test_ats_accepts_projects_instead_of_experience():
    data = make_docx(["Name", "Skills", "Projects", "Education"])
    result = check_ats_compatibility("cv.docx", data, ["skills", "projects", "education"])
    assert result["issues"] == []
    assert result["formatting_score"] == 100


def test_ats_flags_missing_everything():
    data = make_docx(["Name", "just some text"])
    result = check_ats_compatibility("cv.docx", data, [])
    assert len(result["issues"]) >= 2
