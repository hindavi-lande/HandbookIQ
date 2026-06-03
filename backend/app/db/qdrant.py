"""
app/db/qdrant.py
Qdrant client wrapper – collection bootstrap + health check.
"""
from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings

_settings = get_settings()

# Dimension of all-MiniLM-L6-v2  →  384
# Change if you swap the embedding model.
VECTOR_SIZE = 384


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=_settings.qdrant_host, port=_settings.qdrant_port)


def init_collection() -> None:
    """Create the Qdrant collection if it doesn't exist yet."""
    client = get_qdrant_client()
    existing = {c.name for c in client.get_collections().collections}

    if _settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=_settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(
                size=VECTOR_SIZE,
                distance=qmodels.Distance.COSINE,
            ),
        )


def check_qdrant() -> tuple[str, str]:
    """
    Returns (status, collection_info).
    status is 'ok' or an error message.
    """
    try:
        client = get_qdrant_client()
        info = client.get_collection(_settings.qdrant_collection)
        return "ok", f"points={info.points_count}"
    except Exception as exc:  # noqa: BLE001
        return str(exc), "unknown"
