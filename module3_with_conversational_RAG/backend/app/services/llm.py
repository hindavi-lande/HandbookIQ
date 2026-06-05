"""
app/services/llm.py
Shared Groq chat model for the RAG LangGraph pipeline.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import get_settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0.2,
        max_tokens=1024,
    )
