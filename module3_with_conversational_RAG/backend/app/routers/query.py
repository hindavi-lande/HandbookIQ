# routes/query.py
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.rag_graph import get_compiled_rag_graph
from app.services.llm import resolve_llm_selection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Query"])


class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    question: str = Field(..., min_length=3, max_length=1000)
    llm_provider: str | None = None
    model_name: str | None = None


class QueryResponse(BaseModel):
    session_id: str
    answer: str


@router.post("/query", response_model=QueryResponse, summary="Multi-turn RAG query with session memory")
async def query(req: QueryRequest):
    rag_graph = get_compiled_rag_graph()
    settings = get_settings()
    resolved_provider, resolved_model = resolve_llm_selection(
        req.llm_provider or settings.llm_provider,
        req.model_name,
    )

    try:
        result = await rag_graph.ainvoke({
            "session_id": req.session_id,
            "question": req.question,
            "llm_provider": resolved_provider,
            "model_name": resolved_model,
            "messages": [],
            "context": "",
            "answer": "",
        })
    except Exception as exc:
        logger.exception("RAG graph error for session %s", req.session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {exc}",
        ) from exc

    return QueryResponse(
        session_id=req.session_id,
        answer=result["answer"],
    )
