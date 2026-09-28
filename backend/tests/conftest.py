import io
import os
import tempfile

# Point the app at a throwaway SQLite file BEFORE the app is imported.
_tmpdir = tempfile.mkdtemp(prefix="resumefit_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmpdir, 'test.db')}"
os.environ.pop("ANTHROPIC_API_KEY", None)

import pytest
from docx import Document
from fastapi.testclient import TestClient

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def make_docx(lines, table=False) -> bytes:
    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    if table:
        t = doc.add_table(rows=1, cols=2)
        t.rows[0].cells[0].text = "Skill"
        t.rows[0].cells[1].text = "Level"
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


STRONG_RESUME = [
    "Ahmed Raza", "ahmed@email.com | 0300-1234567", "",
    "Skills", "Python, FastAPI, Django, PostgreSQL, Git, Docker, React, Redis", "",
    "Experience",
    "Jan 2023 - Present  Backend Developer, TechCorp",
    "Built REST APIs using FastAPI and PostgreSQL",
    "Used Docker for containerization and Redis for caching", "",
    "Education", "2020 - 2024  BS Computer Science, UET Lahore",
]

WEAK_RESUME = [
    "Sara Khan", "sara@email.com | 0311-9876543", "",
    "Skills", "Photoshop, Illustrator, Figma, Canva", "",
    "Experience",
    "Jun 2024 - Present  Graphic Designer, DesignHub",
    "Created marketing visuals and brand assets", "",
    "Education", "2021 - 2025  BFA Fine Arts, NCA Lahore",
]

STUDENT_RESUME = [
    "Bilal Ahmed", "bilal@email.com", "",
    "PROFILE", "Final year CS student.", "",
    "TECHNICAL SKILLS", "Python, PyTorch, OpenCV, Git", "",
    "PROJECTS",
    "Object Detection and Tracking, Internship",
    "YOLO detection with custom tracking.", "",
    "EDUCATION", "BS Computer Science, University of Lahore, Expected 2027",
]

JD_PYTHON = (
    "We are looking for a Python Developer with 2-4 years of experience.\n"
    "Responsibilities:\n- Build REST APIs using FastAPI or Django\n"
    "- Work with PostgreSQL and Redis\n- Collaborate with the React frontend team\n"
    "Requirements:\n- Strong experience with Python, SQL, Git, Docker\n"
)


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c
