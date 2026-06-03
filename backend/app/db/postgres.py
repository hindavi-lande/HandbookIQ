"""
app/db/postgres.py
SQLAlchemy engine + session factory for PostgreSQL.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.db_models import Base

_settings = get_settings()

engine = create_engine(
    _settings.postgres_url,
    pool_pre_ping=True,       # drop stale connections
    pool_size=5,
    max_overflow=10,
    echo=(_settings.app_env == "development"),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables (idempotent)."""
    Base.metadata.create_all(bind=engine)


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
    """Yield a database session; always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# FastAPI dependency
def db_dependency() -> Generator[Session, None, None]:
    with get_db() as session:
        yield session
