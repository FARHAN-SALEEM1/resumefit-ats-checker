"""Skill gap analysis — pure set comparison, no model needed."""


def analyze_skill_gap(resume_skills: list, jd_required_skills: list) -> dict:
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_required_skills)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)  # resume has these, JD didn't ask — informational

    if len(jd_set) == 0:
        match_percentage = None  # can't score against zero requirements
    else:
        match_percentage = round(len(matched) / len(jd_set) * 100, 1)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "match_percentage": match_percentage,
    }
