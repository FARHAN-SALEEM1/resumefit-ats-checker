from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter(prefix="/analyses", tags=["history"])


def _snippet(text: str, length: int = 70) -> str:
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= length else one_line[:length].rstrip() + "…"


@router.get("")
def list_analyses(user_id: int = 1, db: Session = Depends(get_db)):
    """All past analyses for a user, newest first."""
    rows = (
        db.query(models.Analysis, models.Resume, models.JobDescription)
        .join(models.Resume, models.Analysis.resume_id == models.Resume.id)
        .join(models.JobDescription, models.Analysis.jd_id == models.JobDescription.id)
        .filter(models.Resume.user_id == user_id)
        .order_by(models.Analysis.id.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "resume_id": r.id,
            "resume_filename": r.filename,
            "jd_id": jd.id,
            "jd_snippet": _snippet(jd.raw_text),
            "score": a.score,
            "created_at": a.created_at,
        }
        for a, r, jd in rows
    ]


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Full stored result for one past analysis, in the same shape /analyze returns."""
    row = (
        db.query(models.Analysis, models.Resume, models.JobDescription)
        .join(models.Resume, models.Analysis.resume_id == models.Resume.id)
        .join(models.JobDescription, models.Analysis.jd_id == models.JobDescription.id)
        .filter(models.Analysis.id == analysis_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    a, r, jd = row
    result = dict(a.breakdown_json or {})
    result["analysis_id"] = a.id
    result["resume_filename"] = r.filename
    result["jd_snippet"] = _snippet(jd.raw_text)
    result["created_at"] = a.created_at
    return result
