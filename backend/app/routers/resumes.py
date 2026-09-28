from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.utils.file_extract import extract_text, ExtractionError
from app.parsers.resume_parser import parse_resume
from app.matching.ats_checker import check_ats_compatibility

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _get_or_create_default_user(db: Session, user_id: int) -> models.User:
    """MVP has no auth — auto-create the user row if it doesn't exist yet."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        user = models.User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Form(default=1),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    try:
        raw_text = extract_text(file.filename, file_bytes)
        parsed = parse_resume(raw_text)
        # ATS structural check needs the original file bytes (tables/images
        # aren't visible in plain extracted text), so it runs here at
        # upload time and gets merged into the same parsed_json blob.
        ats_result = check_ats_compatibility(file.filename, file_bytes, parsed["sections_found"])
        parsed["ats_check"] = ats_result
    except ExtractionError as e:
        # Graceful, clear error — not a 500 crash (per brief's constraint).
        raise HTTPException(status_code=422, detail=str(e))

    _get_or_create_default_user(db, user_id)

    resume = models.Resume(
        user_id=user_id,
        filename=file.filename,
        raw_text=raw_text,
        parsed_json=parsed,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.filename,
        "parsed_json": resume.parsed_json,
        "created_at": resume.created_at,
    }


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {
        "id": resume.id,
        "filename": resume.filename,
        "parsed_json": resume.parsed_json,
        "created_at": resume.created_at,
    }


@router.get("/user/{user_id}")
def list_user_resumes(user_id: int, db: Session = Depends(get_db)):
    resumes = db.query(models.Resume).filter(models.Resume.user_id == user_id).all()
    return [
        {"id": r.id, "filename": r.filename, "created_at": r.created_at}
        for r in resumes
    ]
