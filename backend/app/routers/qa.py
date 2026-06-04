"""
app/routers/qa.py
Endpoints
---------
  POST  /api/ask        – run the LangGraph RAG pipeline
  GET   /api/history    – fetch recent Q&A logs from Postgres
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import db_dependency
from app.graph.pipeline import run_qa_pipeline
from app.models.db_models import QALog
from app.models.schemas import AskRequest, AskResponse, SourceChunk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Q&A"])


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about the company handbook",
)
def ask(request: AskRequest, db: Session = Depends(db_dependency)):
    """
    1. Run the LangGraph pipeline (retrieve → generate → format).
    2. Persist the interaction to PostgreSQL.
    3. Return the structured response.
    """
    try:
        result = run_qa_pipeline(
            question=request.question,
            top_k=request.top_k,
            session_id=request.session_id,
        )
    except Exception as exc:
        logger.exception("Pipeline error for question: %s", request.question)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline error: {exc}",
        )

    # ── Persist to PostgreSQL ──────────────────────────────────────────────
    retrieved_ids = ",".join(s["chunk_id"] for s in result.get("sources", []))
    db_log = QALog(
        session_id=request.session_id,
        question=request.question,
        answer=result["answer"],
        top_k=request.top_k,
        retrieved_chunk_ids=retrieved_ids,
        created_at=datetime.utcnow(),
    )
    db.add(db_log)
    db.commit()

    # ── Build response ─────────────────────────────────────────────────────
    sources = [SourceChunk(**s) for s in result.get("sources", [])]
    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        sources=sources,
        session_id=result.get("session_id"),
    )


@router.get(
    "/history",
    summary="Retrieve recent Q&A log entries",
)
def history(limit: int = 20, db: Session = Depends(db_dependency)):
    """Return the most recent *limit* Q&A interactions."""
    logs = (
        db.query(QALog)
        .order_by(QALog.created_at.desc().nulls_last())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(log.id),
            "session_id": log.session_id,
            "question": log.question,
            "answer": log.answer,
            "created_at": (log.created_at or datetime.utcnow()).isoformat(),
        }
        for log in logs
    ]
