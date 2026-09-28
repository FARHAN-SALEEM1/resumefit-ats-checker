from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.matching.gap_analysis import analyze_skill_gap
from app.feedback.prompt_builder import collect_bullets_with_ids, build_feedback_prompt
from app.feedback.claude_client import call_claude_for_feedback, FeedbackGenerationError
from app.feedback.validator import validate_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    resume_id: int
    jd_id: int


@router.post("")
def generate_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == payload.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    jd = db.query(models.JobDescription).filter(models.JobDescription.id == payload.jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")

    resume_parsed = resume.parsed_json
    jd_parsed = jd.parsed_json

    # Recompute gap analysis deterministically — same as Sprint 2, not
    # something Claude decides. This is the ground truth for missing skills.
    gap = analyze_skill_gap(
        resume_skills=resume_parsed.get("skills", []),
        jd_required_skills=jd_parsed.get("required_skills", []),
    )
    missing_skills = gap["missing_skills"]

    known_bullets = collect_bullets_with_ids(resume_parsed.get("experience", []))

    prompt = build_feedback_prompt(
        resume_bullets=known_bullets,
        missing_skills=missing_skills,
        jd_raw_text=jd.raw_text,
    )

    try:
        raw_feedback = call_claude_for_feedback(prompt)
    except FeedbackGenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    validated = validate_feedback(
        raw_feedback=raw_feedback,
        known_bullets=known_bullets,
        allowed_missing_skills=missing_skills,
    )

    return {
        "resume_id": resume.id,
        "jd_id": jd.id,
        "feedback": validated,
    }
