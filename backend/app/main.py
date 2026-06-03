"""
app/main.py
FastAPI application factory.

Startup sequence
----------------
1. Create PostgreSQL tables (idempotent).
2. Bootstrap Qdrant collection (idempotent).
3. Mount routers.
4. Expose /health endpoint.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.postgres import check_postgres, init_db
from app.db.qdrant import check_qdrant, init_collection
from app.models.schemas import HealthResponse
from app.routers import ingest, qa

# ── Logging ───────────────────────────────────────────────────────────────────
_settings = get_settings()
logging.basicConfig(
    level=_settings.log_level.upper(),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="Company Handbook Q&A API",
        description=(
            "RAG-powered Q&A assistant backed by LangGraph, Groq, "
            "Qdrant, and PostgreSQL."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS (allow Next.js dev server) ───────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Startup ───────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Initialising PostgreSQL tables …")
        init_db()
        logger.info("Bootstrapping Qdrant collection …")
        init_collection()
        logger.info("Application ready.")

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(qa.router)
    app.include_router(ingest.router)

    # ── Health ────────────────────────────────────────────────────────────────
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Check service connectivity",
    )
    def health() -> HealthResponse:
        pg_status = check_postgres()
        qdrant_status, collection_info = check_qdrant()
        return HealthResponse(
            status="ok" if pg_status == "ok" and qdrant_status == "ok" else "degraded",
            postgres=pg_status,
            qdrant=qdrant_status,
            collection=collection_info,
        )

    return app


app = create_app()


# ── Dev entry-point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=_settings.log_level,
    )
