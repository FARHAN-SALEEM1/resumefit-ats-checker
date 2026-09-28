"""
Semantic similarity between resume and job description text.

Uses sentence-transformers (all-MiniLM-L6-v2 — small, fast, free,
runs locally, no API cost). This is intentionally NOT keyword matching:
two texts can score highly similar even with different wording, which
is the whole point (brief explicitly rejected keyword-only matching).

NOTE for local setup: the first time this runs, it downloads the model
(~80MB) from huggingface.co — needs a normal internet connection once.
After that it's cached locally and works offline.
"""
from functools import lru_cache
import numpy as np


@lru_cache(maxsize=1)
def _get_model():
    """Loaded once per process, reused after (model loading is slow)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Returns a 0-100 similarity score between two texts.
    Uses cosine similarity of sentence embeddings, rescaled from
    [-1, 1] to [0, 100] for a friendlier score.
    """
    model = _get_model()
    embeddings = model.encode([text_a, text_b])
    a, b = embeddings[0], embeddings[1]

    cosine = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    # Cosine sim for real text pairs rarely goes negative in practice,
    # but clamp defensively before rescaling.
    cosine = max(-1.0, min(1.0, cosine))
    score_0_100 = (cosine + 1) / 2 * 100
    return round(score_0_100, 1)
