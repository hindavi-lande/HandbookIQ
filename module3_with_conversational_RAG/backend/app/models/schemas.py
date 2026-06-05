"""
app/models/schemas.py
Pydantic v2 models for all API request / response bodies.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Ingest ────────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Optional override; if omitted the server scans data/handbook/."""
    directory: Optional[str] = Field(
        default=None,
        description="Absolute or relative path to a folder of .txt / .pdf files.",
    )


class ChunkMeta(BaseModel):
    chunk_id: str
    source_file: str
    chunk_index: int
    char_count: int


class IngestResponse(BaseModel):
    message: str
    total_chunks: int
    chunks: List[ChunkMeta]


# ── Q&A ───────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=10)
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for conversation history.",
    )


class SourceChunk(BaseModel):
    chunk_id: str
    source_file: str
    score: float
    excerpt: str          # first 300 chars of the chunk


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceChunk]
    session_id: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    postgres: str
    qdrant: str
    collection: str
