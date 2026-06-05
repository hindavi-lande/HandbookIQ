"""
app/db/postgres.py
SQLAlchemy sync + async engines and session factories for PostgreSQL.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.db_models import Base

_settings = get_settings()

engine = create_engine(
    _settings.postgres_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=(_settings.app_env == "development"),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

async_engine = create_async_engine(
    _settings.postgres_async_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=(_settings.app_env == "development"),
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


def _migrate_qa_logs_created_at() -> None:
    """Backfill NULL timestamps and enforce NOT NULL on qa_logs.created_at."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE qa_logs SET created_at = CURRENT_TIMESTAMP "
                "WHERE created_at IS NULL"
            )
        )
        conn.execute(
            text("ALTER TABLE qa_logs ALTER COLUMN created_at SET NOT NULL")
        )
        conn.execute(
            text(
                "ALTER TABLE qa_logs ALTER COLUMN created_at "
                "SET DEFAULT CURRENT_TIMESTAMP"
            )
        )


def init_db() -> None:
    """Create all tables (idempotent) and apply lightweight schema fixes."""
    Base.metadata.create_all(bind=engine)
    _migrate_qa_logs_created_at()


def check_postgres() -> str:
    """Return 'ok' or an error string."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return str(exc)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Yield a sync database session; always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def db_dependency() -> Generator[Session, None, None]:
    """FastAPI dependency for sync sessions."""
    with get_db() as session:
        yield session


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session; commit/rollback and close on exit."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def async_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async sessions."""
    async with get_async_db() as session:
        yield session


async def dispose_async_engine() -> None:
    """Release async connection pool resources on application shutdown."""
    await async_engine.dispose()
