"""
app/config.py
Centralised application settings loaded from environment variables / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── LLM provider switching ─────────────────────────────────────────────────
    llm_provider: str = "groq"  # groq | openai | ollama

    # ── Groq ──────────────────────────────────────────────────────────────────
    groq_api_key: str
    groq_model: str = "llama3-70b-8192"

    # ── OpenAI ────────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "handbook_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Qdrant ────────────────────────────────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "handbook_chunks"

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "info"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""
    return Settings()
