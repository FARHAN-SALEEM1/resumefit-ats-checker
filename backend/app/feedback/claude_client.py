"""
Thin wrapper around the Anthropic API for feedback generation.

Requires ANTHROPIC_API_KEY as an environment variable — never hardcode
a key in source. Get one from https://console.anthropic.com

Model default is Haiku (cheap, fast) since this is short structured
feedback, not long-form generation — keeps per-request cost low for
an MVP on a free/cheap hosting tier. Override with ANTHROPIC_MODEL env
var if you want higher-quality phrasing (e.g. a Sonnet-tier model) and
are OK with the extra cost.
"""
import os
import json


class FeedbackGenerationError(Exception):
    pass


def call_claude_for_feedback(prompt: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise FeedbackGenerationError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Get a key from https://console.anthropic.com and set it "
            "before starting the server."
        )

    try:
        import anthropic
    except ImportError:
        raise FeedbackGenerationError(
            "The 'anthropic' package is not installed. Run: pip install anthropic"
        )

    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        raise FeedbackGenerationError(f"Claude API call failed: {e}")

    raw_text = "".join(block.text for block in response.content if hasattr(block, "text"))

    # Defensive cleanup in case the model wraps output in a code fence
    # despite instructions not to.
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise FeedbackGenerationError(f"Claude returned non-JSON output: {e}. Raw: {raw_text[:300]}")
