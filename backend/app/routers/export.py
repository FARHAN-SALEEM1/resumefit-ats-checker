from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io

from app.database import get_db
from app import models
from app.export.resume_pdf import build_resume_pdf

router = APIRouter(prefix="/export-resume", tags=["export"])


class ExportRequest(BaseModel):
    resume_id: int
    bullet_rewrites: list = []  # pass the validated rewrites from a /feedback response, if any


@router.post("")
def export_resume(payload: ExportRequest, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == payload.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        pdf_bytes = build_resume_pdf(resume.parsed_json, payload.bullet_rewrites)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not generate PDF: {e}")

    filename = f"resume_improved_{resume.id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
