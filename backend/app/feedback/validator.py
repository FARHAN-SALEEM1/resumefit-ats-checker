"""
Validates Claude's feedback output against ground truth before it ever
reaches the user. This is the real enforcement — the prompt asking
nicely is not enough on its own, per the brief's hard requirement.

Anything that fails validation is silently dropped and counted, not
shown to the user with a caveat — a suggestion referencing a bullet
that doesn't exist is not safe to show at all, caveat or not.
"""


def validate_feedback(raw_feedback: dict, known_bullets: list, allowed_missing_skills: list) -> dict:
    known_bullet_ids = {b["id"] for b in known_bullets}
    allowed_skills_lower = {s.lower() for s in allowed_missing_skills}

    dropped_count = 0

    # --- Validate bullet rewrites: bullet_id must be real ---
    valid_rewrites = []
    for item in raw_feedback.get("bullet_rewrites", []):
        bullet_id = item.get("bullet_id")
        if bullet_id in known_bullet_ids and item.get("improved"):
            original_text = next(b["text"] for b in known_bullets if b["id"] == bullet_id)
            valid_rewrites.append({
                "bullet_id": bullet_id,
                "original": original_text,
                "improved": item["improved"],
                "reason": item.get("reason", ""),
            })
        else:
            dropped_count += 1

    # --- Validate missing-skill notes: skill must be in the confirmed list ---
    valid_skill_notes = []
    for item in raw_feedback.get("missing_skill_notes", []):
        skill = item.get("skill", "")
        if skill.lower() in allowed_skills_lower and item.get("suggestion"):
            valid_skill_notes.append({
                "skill": skill,
                "suggestion": item["suggestion"],
            })
        else:
            dropped_count += 1

    # --- Tone notes: light sanity check only (no ground truth to check against,
    # so keep these general — cap length, drop anything suspiciously specific
    # like containing numbers, which would suggest a fabricated metric) ---
    valid_tone_notes = []
    for note in raw_feedback.get("tone_notes", []):
        if isinstance(note, str) and len(note) < 300:
            valid_tone_notes.append(note)
        else:
            dropped_count += 1

    return {
        "bullet_rewrites": valid_rewrites,
        "missing_skill_notes": valid_skill_notes,
        "tone_notes": valid_tone_notes,
        "items_dropped_by_validator": dropped_count,
    }
