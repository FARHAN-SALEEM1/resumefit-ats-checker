"""
Builds the prompt sent to Claude for feedback generation.

Key anti-hallucination design choice: we do NOT ask Claude to figure
out which skills are missing — that's already computed deterministically
by app/matching/gap_analysis.py in Sprint 2. Claude's job here is
narrower: (1) suggest better phrasing for bullets that ACTUALLY EXIST
in the resume, referenced by ID so we can verify them, and (2) write
one actionable sentence per already-confirmed missing skill.
This shrinks the surface area where fabrication could happen.
"""


def collect_bullets_with_ids(experience_entries: list) -> list:
    """
    Flattens resume experience entries into {id, text} pairs.
    IDs are simple and stable within one request (b0, b1, b2...) so
    Claude can reference them and we can verify the reference is real.
    """
    bullets = []
    counter = 0
    for entry in experience_entries:
        header = entry.get("header", "")
        for bullet_text in entry.get("bullets", []):
            bullets.append({"id": f"b{counter}", "text": bullet_text, "context": header})
            counter += 1
    return bullets


def build_feedback_prompt(resume_bullets: list, missing_skills: list, jd_raw_text: str) -> str:
    bullets_block = "\n".join(f"[{b['id']}] {b['text']}" for b in resume_bullets) or "(no bullet points found)"
    missing_block = ", ".join(missing_skills) if missing_skills else "(none — resume covers all detected required skills)"

    prompt = f"""You are helping a job seeker improve their resume for a specific job application.

STRICT RULES (do not break these):
1. You may ONLY rewrite bullet points that are given to you below, referenced by their exact ID. Do not invent new bullets or reference IDs that don't exist.
2. You may ONLY discuss missing skills from the exact list given below. Do not suggest any other skill.
3. Never claim or imply the candidate already has a skill, tool, or achievement that is not stated in their bullet points below. For missing skills, phrase suggestions as "consider adding if applicable" — never as fact.
4. Do not invent company names, numbers, metrics, or achievements. If a bullet lacks a metric, you may suggest the candidate add one (e.g. "consider quantifying the impact"), but never invent a specific number yourself.
5. Output ONLY valid JSON, no other text, no markdown code fences.

RESUME BULLET POINTS (only these exist — reference by ID):
{bullets_block}

MISSING SKILLS (confirmed by separate analysis — only discuss these):
{missing_block}

JOB DESCRIPTION (for context on tone/priorities only):
{jd_raw_text[:2000]}

Return JSON in exactly this shape:
{{
  "bullet_rewrites": [
    {{"bullet_id": "b0", "improved": "rewritten version, same facts, stronger phrasing", "reason": "why this is better"}}
  ],
  "missing_skill_notes": [
    {{"skill": "exact skill from the missing list", "suggestion": "Consider adding ... if you have relevant experience"}}
  ],
  "tone_notes": ["short, general observations about clarity/tone — no fabricated specifics"]
}}

Only include bullet_rewrites for bullets that genuinely benefit from improvement (weak verbs, vague phrasing, no impact stated) — don't force a rewrite for every bullet if it's already good."""
    return prompt
