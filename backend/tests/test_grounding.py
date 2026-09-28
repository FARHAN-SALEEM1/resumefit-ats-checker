"""The no-fabrication guarantee: the validator must drop anything that isn't
traceable to the resume or to the deterministic gap analysis."""
from app.feedback.prompt_builder import collect_bullets_with_ids, build_feedback_prompt
from app.feedback.validator import validate_feedback

EXPERIENCE = [{"header": "Jan 2023 - Present Dev", "bullets": ["worked on backend", "helped the team"]}]


def test_bullet_ids_are_stable_and_ordered():
    bullets = collect_bullets_with_ids(EXPERIENCE)
    assert [b["id"] for b in bullets] == ["b0", "b1"]


def test_validator_drops_fabricated_bullet_and_skill():
    bullets = collect_bullets_with_ids(EXPERIENCE)
    raw = {
        "bullet_rewrites": [
            {"bullet_id": "b0", "improved": "Built backend services", "reason": "specific"},
            {"bullet_id": "b99", "improved": "Led 10 engineers", "reason": "invented"},
        ],
        "missing_skill_notes": [
            {"skill": "docker", "suggestion": "Consider adding Docker if applicable."},
            {"skill": "kubernetes", "suggestion": "Not in the confirmed list."},
        ],
        "tone_notes": ["Add measurable impact where you can."],
    }
    out = validate_feedback(raw, bullets, allowed_missing_skills=["docker"])
    assert [r["bullet_id"] for r in out["bullet_rewrites"]] == ["b0"]
    assert out["bullet_rewrites"][0]["original"] == "worked on backend"
    assert [n["skill"] for n in out["missing_skill_notes"]] == ["docker"]
    assert out["items_dropped_by_validator"] == 2


def test_validator_survives_malformed_items():
    bullets = collect_bullets_with_ids(EXPERIENCE)
    raw = {"bullet_rewrites": [{}], "missing_skill_notes": [{"skill": "docker"}], "tone_notes": [123]}
    out = validate_feedback(raw, bullets, allowed_missing_skills=["docker"])
    assert out["bullet_rewrites"] == []
    assert out["missing_skill_notes"] == []
    assert out["tone_notes"] == []


def test_prompt_contains_only_allowed_material():
    bullets = collect_bullets_with_ids(EXPERIENCE)
    prompt = build_feedback_prompt(bullets, ["docker"], "Job text")
    assert "[b0] worked on backend" in prompt
    assert "docker" in prompt
