"""
app/services/retriever.py
Semantic retrieval from Qdrant using cosine similarity.

Returns ranked SourceChunk objects ready for the LangGraph pipeline.
"""
from __future__ import annotations

import logging
from typing import List

from app.config import get_settings
from app.db.qdrant import get_qdrant_client
from app.models.schemas import SourceChunk
from app.services.embeddings import embed_query

logger = logging.getLogger(__name__)
_settings = get_settings()

_EXCERPT_MAX = 300   # characters shown in the response


def retrieve(question: str, top_k: int = 4) -> List[SourceChunk]:
    """
    Embed *question*, query Qdrant for the top-k most similar chunks,
    and return them as SourceChunk objects sorted by descending score.
    """
    query_vector = embed_query(question)
    client = get_qdrant_client()

    results = client.search(
        collection_name=_settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    chunks: List[SourceChunk] = []
    for hit in results:
        payload = hit.payload or {}
        content: str = payload.get("content", "")
        chunks.append(
            SourceChunk(
                chunk_id=str(hit.id),
                source_file=payload.get("source_file", "unknown"),
                score=round(float(hit.score), 4),
                excerpt=content[:_EXCERPT_MAX],
            )
        )

    logger.debug("Retrieved %d chunks for query: %.60s…", len(chunks), question)
    return chunks
