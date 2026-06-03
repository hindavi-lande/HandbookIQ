"""
app/graph/state.py
Typed state that flows between LangGraph nodes.

All fields are Optional so each node only mutates what it owns.
"""
from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict

from app.models.schemas import SourceChunk


class QAState(TypedDict, total=False):
    # ── Input ─────────────────────────────────────────────────────────────────
    question: str
    top_k: int
    session_id: Optional[str]

    # ── Set by retriever_node ─────────────────────────────────────────────────
    retrieved_chunks: List[SourceChunk]

    # ── Set by generator_node ─────────────────────────────────────────────────
    answer: str

    # ── Set by formatter_node ─────────────────────────────────────────────────
    structured_response: dict  # serialised AskResponse

    # ── Error propagation ─────────────────────────────────────────────────────
    error: Optional[str]
