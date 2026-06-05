"""
app/services/embeddings.py
Thin wrapper around SentenceTransformers.

Why local embeddings?
  • No extra API key or cost per call.
  • all-MiniLM-L6-v2 is fast (~80 ms/batch on CPU) and good enough for
    handbook-scale corpora (< 10 k chunks).
  • Swap for OpenAI / Cohere embeddings later without touching other code.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import get_settings

_settings = get_settings()


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load the model once and cache in memory."""
    return SentenceTransformer(_settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Encode a list of strings and return a list of float vectors.
    All vectors share the same dimension (384 for MiniLM-L6-v2).
    """
    model = _get_model()
    vectors = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(query: str) -> List[float]:
    """Convenience wrapper for single-query embedding."""
    return embed_texts([query])[0]
