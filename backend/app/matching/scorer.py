"""
Combines skill match, experience match, and ATS formatting into one
0-100 score with a visible breakdown — per Sprint 2 acceptance criteria.

Weights (documented, easy to tune later):
  - Keyword/skill match: 50%
  - Experience match:    30%
  - ATS formatting:      20%
"""
import re
import datetime

LEVEL_ORDER = {"entry": 0, "junior": 1, "mid": 2, "senior": 3}
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
CURRENT_YEAR = datetime.date.today().year


def estimate_experience_years(experience_entries: list) -> float:
    """
    Rough proxy: look at every year mentioned across all experience
    entry headers, take (latest - earliest). Not precise (doesn't
    account for gaps/overlaps) — documented MVP heuristic, good enough
    to bucket into entry/junior/mid/senior.
    """
    years_found = []
    for entry in experience_entries:
        header = entry.get("header", "")
        if "present" in header.lower() or "current" in header.lower():
            years_found.append(CURRENT_YEAR)
        for match in YEAR_RE.finditer(header):
            years_found.append(int(match.group(0)))

    if not years_found:
        return 0.0
    return max(0.0, float(max(years_found) - min(years_found)))


def estimate_level_from_years(years: float) -> str:
    if years < 1:
        return "entry"
    elif years < 3:
        return "junior"
    elif years < 5:
        return "mid"
    else:
        return "senior"


def score_experience_match(resume_experience: list, jd_experience_level: str | None) -> dict:
    estimated_years = estimate_experience_years(resume_experience)
    resume_level = estimate_level_from_years(estimated_years)

    if not jd_experience_level or jd_experience_level not in LEVEL_ORDER:
        return {
            "score": 70,  # neutral default — nothing to compare against
            "estimated_resume_years": estimated_years,
            "estimated_resume_level": resume_level,
            "jd_required_level": None,
            "note": "JD did not specify a clear experience level — score is a neutral default.",
        }

    diff = abs(LEVEL_ORDER[resume_level] - LEVEL_ORDER[jd_experience_level])
    score_by_diff = {0: 100, 1: 70, 2: 40}
    score = score_by_diff.get(diff, 20)

    return {
        "score": score,
        "estimated_resume_years": estimated_years,
        "estimated_resume_level": resume_level,
        "jd_required_level": jd_experience_level,
        "note": None,
    }


def compute_final_score(keyword_match_pct, experience_score: float, formatting_score: float) -> dict:
    """
    keyword_match_pct can be None if the JD had no detected required
    skills — in that case its weight is redistributed to the other two.
    """
    if keyword_match_pct is None:
        combined = round(experience_score * 0.6 + formatting_score * 0.4, 1)
        weights_used = {"keyword_match": 0, "experience_match": 60, "formatting": 40}
    else:
        combined = round(keyword_match_pct * 0.5 + experience_score * 0.3 + formatting_score * 0.2, 1)
        weights_used = {"keyword_match": 50, "experience_match": 30, "formatting": 20}

    return {
        "overall_score": combined,
        "breakdown": {
            "keyword_match": keyword_match_pct,
            "experience_match": experience_score,
            "formatting_score": formatting_score,
        },
        "weights_used": weights_used,
    }
