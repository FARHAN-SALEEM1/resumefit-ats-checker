from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.matching.embeddings import compute_similarity
from app.matching.gap_analysis import analyze_skill_gap
from app.matching.scorer import score_experience_match, compute_final_score

router = APIRouter(prefix="/analyze", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    resume_id: int
    jd_id: int


@router.post("")
def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == payload.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    jd = db.query(models.JobDescription).filter(models.JobDescription.id == payload.jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")

    resume_parsed = resume.parsed_json
    jd_parsed = jd.parsed_json

    # 1. Semantic similarity (embeddings) — whole-text comparison, not just keywords.
    semantic_similarity = compute_similarity(resume.raw_text, jd.raw_text)

    # 2. Skill gap analysis — explicit matched/missing skill lists.
    gap = analyze_skill_gap(
        resume_skills=resume_parsed.get("skills", []),
        jd_required_skills=jd_parsed.get("required_skills", []),
    )

    # 3. Experience level match.
    experience_result = score_experience_match(
        resume_experience=resume_parsed.get("experience", []),
        jd_experience_level=jd_parsed.get("experience_level"),
    )

    # 4. ATS formatting score (computed at upload time, stored on the resume).
    ats_check = resume_parsed.get("ats_check", {"issues": [], "formatting_score": 70})

    # Combine keyword match (from gap analysis) with semantic similarity:
    # average them so a resume can't game the score with keyword-stuffing
    # alone (brief's explicit constraint) while still rewarding real overlap.
    keyword_pct = gap["match_percentage"]
    if keyword_pct is not None:
        blended_keyword_score = round((keyword_pct + semantic_similarity) / 2, 1)
    else:
        blended_keyword_score = None

    final = compute_final_score(
        keyword_match_pct=blended_keyword_score,
        experience_score=experience_result["score"],
        formatting_score=ats_check["formatting_score"],
    )

    result = {
        "resume_id": resume.id,
        "jd_id": jd.id,
        "overall_score": final["overall_score"],
        "breakdown": final["breakdown"],
        "weights_used": final["weights_used"],
        "semantic_similarity": semantic_similarity,
        "skill_gap": gap,
        "experience_match": experience_result,
        "ats_formatting": ats_check,
    }

    analysis_row = models.Analysis(
        resume_id=resume.id,
        jd_id=jd.id,
        score=final["overall_score"],
        breakdown_json=result,
    )
    db.add(analysis_row)
    db.commit()
    db.refresh(analysis_row)

    result["analysis_id"] = analysis_row.id
    return result
