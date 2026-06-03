"""
app/routers/ingest.py
Endpoints
---------
  POST  /api/ingest     – load documents from data/handbook/ (or a custom path)
  GET   /api/documents  – list ingested documents from Postgres
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres import db_dependency
from app.models.db_models import Document
from app.models.schemas import IngestRequest, IngestResponse
from app.services.ingestion import ingest_directory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Ingestion"])


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest handbook documents into Qdrant + PostgreSQL",
)
def ingest(
    request: IngestRequest = IngestRequest(),
    db: Session = Depends(db_dependency),
):
    """
    Walk the handbook directory, split every .txt / .pdf into chunks,
    embed them, and upsert into Qdrant.  Metadata is stored in PostgreSQL.

    - If `directory` is omitted the server uses `data/handbook/`.
    - Re-ingesting the same file replaces its existing chunks.
    """
    try:
        total, chunks = ingest_directory(db=db, directory=request.directory)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion error: {exc}",
        )

    return IngestResponse(
        message=f"Successfully ingested {total} chunks.",
        total_chunks=total,
        chunks=chunks,
    )


@router.get(
    "/documents",
    summary="List all ingested source documents",
)
def list_documents(db: Session = Depends(db_dependency)):
    docs = db.query(Document).order_by(Document.ingested_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "file_path": d.file_path,
            "chunk_count": len(d.chunks),
            "ingested_at": d.ingested_at.isoformat(),
        }
        for d in docs
    ]
