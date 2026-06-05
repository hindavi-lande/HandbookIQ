# routes/query.py
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.graph.rag_graph import get_compiled_rag_graph

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Query"])


class QueryRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    question: str = Field(..., min_length=3, max_length=1000)


class QueryResponse(BaseModel):
    session_id: str
    answer: str


@router.post("/query", response_model=QueryResponse, summary="Multi-turn RAG query with session memory")
async def query(req: QueryRequest):
    rag_graph = get_compiled_rag_graph()

    try:
        result = await rag_graph.ainvoke({
            "session_id": req.session_id,
            "question": req.question,
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
