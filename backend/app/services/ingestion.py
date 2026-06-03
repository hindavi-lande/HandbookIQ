"""
app/services/ingestion.py
Pipeline: load documents → split into chunks → embed → upsert to Qdrant
          → persist metadata to PostgreSQL.

Supported file types
--------------------
  .txt   – plain text, read directly
  .pdf   – extracted via pypdf

Directory layout expected
-------------------------
  data/handbook/
    ├── leave_policy.txt
    ├── code_of_conduct.pdf
    └── benefits.txt
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import List, Tuple

from qdrant_client.http import models as qmodels
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.qdrant import get_qdrant_client
from app.models.db_models import Chunk, Document
from app.models.schemas import ChunkMeta
from app.services.embeddings import embed_texts

logger = logging.getLogger(__name__)
_settings = get_settings()

# Default handbook directory (relative to project root)
DEFAULT_HANDBOOK_DIR = Path(__file__).resolve().parents[2] / "data" / "handbook"


# ── Low-level helpers ─────────────────────────────────────────────────────────


def _read_txt(path: Path) -> str:
    logger.info("About to load file: %s", path)
    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    logger.info("Finished loading file")
    logger.info("STEP B: File loaded")
    logger.info("STEP C: Chars loaded: %s", len(raw_text))
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader  # lazy import – only when needed

    reader = PdfReader(str(path))
    return "\n".join(
        page.extract_text() or "" for page in reader.pages
    )


def _load_file(path: Path) -> str:
    """Dispatch to the correct loader based on file extension."""
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _read_txt(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple sliding-window character splitter.
    Tries to break on the nearest newline to avoid cutting mid-sentence.
    """
    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to end at a newline for cleaner splits
        if end < text_len:
            nl_pos = text.rfind("\n", start, end)
            if nl_pos > start:
                end = nl_pos + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == text_len:
            break

        start = end - overlap  # slide back by overlap
        logger.info("start=%s end=%s", start, end)

    return chunks


# ── Main ingestion function ───────────────────────────────────────────────────

def ingest_directory(
    db: Session,
    directory: str | None = None,
) -> Tuple[int, List[ChunkMeta]]:
    """
    Walk *directory* (defaults to data/handbook/), load every .txt / .pdf,
    split into chunks, embed, upsert to Qdrant, persist to PostgreSQL.

    Returns (total_chunks, list[ChunkMeta]).
    """
    doc_dir = Path(directory) if directory else DEFAULT_HANDBOOK_DIR
    if not doc_dir.exists():
        raise FileNotFoundError(f"Handbook directory not found: {doc_dir}")

    supported = {".txt", ".pdf"}
    files = [f for f in doc_dir.iterdir() if f.suffix.lower() in supported]

    if not files:
        raise ValueError(f"No .txt or .pdf files found in {doc_dir}")

    qdrant = get_qdrant_client()
    all_meta: List[ChunkMeta] = []

    for file_path in sorted(files):
        logger.info("Ingesting %s …", file_path.name)

        # ── Load raw text ──────────────────────────────────────────────────
        try:
            raw_text = _load_file(file_path)
        except Exception as exc:
            logger.error("Failed to load %s: %s", file_path.name, exc)
            continue

        if not raw_text.strip():
            logger.warning("Empty content in %s, skipping.", file_path.name)
            continue

        # ── Split ──────────────────────────────────────────────────────────
        chunks = _split_text(
            raw_text,
            chunk_size=_settings.chunk_size,
            overlap=_settings.chunk_overlap,
        )

        # ── Postgres: upsert Document row ──────────────────────────────────
        db_doc = (
            db.query(Document)
            .filter(Document.file_path == str(file_path))
            .first()
        )
        if db_doc is None:
            db_doc = Document(
                filename=file_path.name,
                file_path=str(file_path),
            )
            db.add(db_doc)
            db.flush()  # get db_doc.id before creating chunks
        else:
            # Re-ingestion: delete old chunks then re-create
            db.query(Chunk).filter(Chunk.document_id == db_doc.id).delete()
            db.flush()

        logger.info("Loaded %s characters", len(raw_text))
        logger.info("Created %s chunks", len(chunks))
        # ── Embed all chunks in one batch ──────────────────────────────────
        vectors = embed_texts(chunks)
        logger.info("Generated %s vectors", len(vectors))

        

        # ── Build Qdrant points + Postgres chunks ──────────────────────────
        qdrant_points: List[qmodels.PointStruct] = []
        file_meta: List[ChunkMeta] = []

        for idx, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
            chunk_uuid = uuid.uuid4()

            # Postgres
            db_chunk = Chunk(
                id=chunk_uuid,
                document_id=db_doc.id,
                chunk_index=idx,
                content=chunk_text,
                char_count=len(chunk_text),
            )
            db.add(db_chunk)

            # Qdrant payload carries everything needed for display
            qdrant_points.append(
                qmodels.PointStruct(
                    id=str(chunk_uuid),
                    vector=vector,
                    payload={
                        "source_file": file_path.name,
                        "chunk_index": idx,
                        "document_id": str(db_doc.id),
                        "content": chunk_text,
                    },
                )
            )

            file_meta.append(
                ChunkMeta(
                    chunk_id=str(chunk_uuid),
                    source_file=file_path.name,
                    chunk_index=idx,
                    char_count=len(chunk_text),
                )
            )

            logger.info("Upserting %s points into %s",
            len(qdrant_points),
            _settings.qdrant_collection)

        # ── Upsert to Qdrant ───────────────────────────────────────────────
        result = qdrant.upsert(
            collection_name=_settings.qdrant_collection,
            points=qdrant_points,
        )
        logger.info("Upsert result: %s", result)

        all_meta.extend(file_meta)
        logger.info("  → %d chunks for %s", len(chunks), file_path.name)

    db.commit()
    return len(all_meta), all_meta
