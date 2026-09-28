"""
Database tables.

Sprint 1 only actively uses User, Resume, JobDescription.
Analysis table is defined now (schema sign-off was requested up front)
but stays empty until Sprint 2.
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resumes = relationship("Resume", back_populates="owner")
    job_descriptions = relationship("JobDescription", back_populates="owner")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=False)  # structured: contact, skills, experience, education, sections
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="resumes")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(JSON, nullable=False)  # structured: required_skills, experience_level, responsibilities
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="job_descriptions")


class Analysis(Base):
    """Sprint 2 territory — table exists now so the schema is complete
    and future migrations don't need to alter existing tables."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    score = Column(Float, nullable=True)
    breakdown_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
