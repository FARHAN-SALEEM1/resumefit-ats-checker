"""Pydantic models — define what the API accepts and returns."""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


# ---------- Resume ----------

class ResumeParsed(BaseModel):
    contact: Dict[str, Optional[str]]       # name, email, phone, linkedin
    skills: List[str]
    experience: List[Dict[str, Any]]        # list of {title, company, dates, bullets}
    education: List[Dict[str, Any]]         # list of {degree, institute, dates}
    sections_found: List[str]               # which standard sections were detected
    warnings: List[str]                     # parsing issues to flag to the user
    ats_check: Optional[Dict[str, Any]] = None  # {issues: [...], formatting_score: int}


class ResumeOut(BaseModel):
    id: int
    filename: str
    parsed_json: ResumeParsed
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Job Description ----------

class JDParsed(BaseModel):
    required_skills: List[str]
    experience_level: Optional[str]         # e.g. "entry", "mid", "senior", or raw text found
    responsibilities: List[str]
    warnings: List[str]


class JDInput(BaseModel):
    raw_text: str
    user_id: int = 1  # MVP: no auth yet, default session user


class JDOut(BaseModel):
    id: int
    parsed_json: JDParsed
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
