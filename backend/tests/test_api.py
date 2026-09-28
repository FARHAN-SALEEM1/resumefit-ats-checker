"""End-to-end API tests through FastAPI's TestClient (embedding model and
Claude API are mocked so the suite runs offline and costs nothing)."""
from unittest.mock import patch

import pytest
from tests.conftest import (
    make_docx, DOCX_MIME, STRONG_RESUME, WEAK_RESUME, JD_PYTHON,
)


def _upload(client, lines, name="cv.docx"):
    r = client.post(
        "/resumes/upload",
        files={"file": (name, make_docx(lines), DOCX_MIME)},
        data={"user_id": 1},
    )
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _jd(client, text=JD_PYTHON):
    r = client.post("/job-descriptions", json={"raw_text": text, "user_id": 1})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _fake_similarity(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return round(min(len(wa & wb) / max(1, len(wb)) * 150, 100), 1)


@pytest.fixture()
def mock_embeddings():
    with patch("app.routers.analysis.compute_similarity", side_effect=_fake_similarity):
        yield


def test_health(client):
    assert client.get("/").json()["status"] == "ok"


def test_corrupt_and_unsupported_files_fail_gracefully(client):
    r = client.post("/resumes/upload", files={"file": ("bad.pdf", b"not a pdf", "application/pdf")}, data={"user_id": 1})
    assert r.status_code == 422
    r = client.post("/resumes/upload", files={"file": ("cv.txt", b"hello", "text/plain")}, data={"user_id": 1})
    assert r.status_code == 422
    r = client.post("/resumes/upload", files={"file": ("empty.pdf", b"", "application/pdf")}, data={"user_id": 1})
    assert r.status_code == 400


def test_short_job_description_rejected(client):
    r = client.post("/job-descriptions", json={"raw_text": "too short", "user_id": 1})
    assert r.status_code == 400


def test_strong_resume_outscores_weak_resume(client, mock_embeddings):
    jd = _jd(client)
    strong = client.post("/analyze", json={"resume_id": _upload(client, STRONG_RESUME, "strong.docx"), "jd_id": jd}).json()
    weak = client.post("/analyze", json={"resume_id": _upload(client, WEAK_RESUME, "weak.docx"), "jd_id": jd}).json()
    assert strong["overall_score"] > weak["overall_score"] + 10
    assert "python" in strong["skill_gap"]["matched_skills"]
    assert "python" in weak["skill_gap"]["missing_skills"]


def test_analyze_unknown_ids_404(client, mock_embeddings):
    assert client.post("/analyze", json={"resume_id": 99999, "jd_id": 1}).status_code == 404


def test_history_lists_and_reopens_analyses(client, mock_embeddings):
    jd = _jd(client)
    rid = _upload(client, STRONG_RESUME, "history_check.docx")
    aid = client.post("/analyze", json={"resume_id": rid, "jd_id": jd}).json()["analysis_id"]

    listing = client.get("/analyses?user_id=1").json()
    assert any(row["id"] == aid and row["resume_filename"] == "history_check.docx" for row in listing)

    full = client.get(f"/analyses/{aid}").json()
    assert full["analysis_id"] == aid
    assert "overall_score" in full and "skill_gap" in full
    assert client.get("/analyses/999999").status_code == 404


def test_feedback_without_api_key_returns_clean_error(client):
    rid = _upload(client, STRONG_RESUME)
    r = client.post("/feedback", json={"resume_id": rid, "jd_id": _jd(client)})
    assert r.status_code == 502
    assert "ANTHROPIC_API_KEY" in r.json()["detail"]


def test_feedback_drops_fabricated_items(client):
    rid = _upload(client, STRONG_RESUME)
    jd = _jd(client, "Python developer wanted. Must know Python, FastAPI and TensorFlow for machine learning work.")
    fake = {
        "bullet_rewrites": [
            {"bullet_id": "b0", "improved": "Built REST APIs with FastAPI and PostgreSQL", "reason": "clearer"},
            {"bullet_id": "b42", "improved": "Managed a team of 50", "reason": "invented"},
        ],
        "missing_skill_notes": [
            {"skill": "tensorflow", "suggestion": "Consider adding TensorFlow if applicable."},
            {"skill": "kubernetes", "suggestion": "invented"},
        ],
        "tone_notes": [],
    }
    with patch("app.routers.feedback.call_claude_for_feedback", return_value=fake):
        body = client.post("/feedback", json={"resume_id": rid, "jd_id": jd}).json()["feedback"]
    assert [r["bullet_id"] for r in body["bullet_rewrites"]] == ["b0"]
    assert [n["skill"] for n in body["missing_skill_notes"]] == ["tensorflow"]
    assert body["items_dropped_by_validator"] == 2


def test_export_pdf_contains_improved_bullet(client):
    import io
    import pdfplumber
    rid = _upload(client, STRONG_RESUME)
    r = client.post("/export-resume", json={
        "resume_id": rid,
        "bullet_rewrites": [{"bullet_id": "b0", "improved": "Designed and shipped REST APIs"}],
    })
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        text = pdf.pages[0].extract_text()
    assert "Designed and shipped REST APIs" in text
    assert "Ahmed Raza" in text


def test_export_without_rewrites_still_works(client):
    rid = _upload(client, STRONG_RESUME)
    assert client.post("/export-resume", json={"resume_id": rid, "bullet_rewrites": []}).status_code == 200
    assert client.post("/export-resume", json={"resume_id": 99999}).status_code == 404
