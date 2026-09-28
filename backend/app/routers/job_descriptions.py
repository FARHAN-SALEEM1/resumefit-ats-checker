from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import JDInput
from app.parsers.jd_parser import parse_job_description

router = APIRouter(prefix="/job-descriptions", tags=["job_descriptions"])


def _get_or_create_default_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        user = models.User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("")
def submit_job_description(payload: JDInput, db: Session = Depends(get_db)):
    if not payload.raw_text or len(payload.raw_text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Job description text is too short to parse meaningfully.",
        )

    parsed = parse_job_description(payload.raw_text)

    _get_or_create_default_user(db, payload.user_id)

    jd = models.JobDescription(
        user_id=payload.user_id,
        raw_text=payload.raw_text,
        parsed_json=parsed,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return {"id": jd.id, "parsed_json": jd.parsed_json, "created_at": jd.created_at}


@router.get("/{jd_id}")
def get_job_description(jd_id: int, db: Session = Depends(get_db)):
    jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return {"id": jd.id, "parsed_json": jd.parsed_json, "created_at": jd.created_at}
