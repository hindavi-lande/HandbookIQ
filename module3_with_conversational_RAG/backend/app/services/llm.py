"""
app/services/llm.py
LLM factory — switch between Groq (cloud), OpenAI (cloud), and Ollama (local).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config import get_settings

LLMProvider = Literal["groq", "openai", "ollama"]

PROVIDER_LABELS: dict[str, str] = {
    "groq": "Groq (Cloud)",
    "openai": "OpenAI (Cloud)",
    "ollama": "Ollama (Local)",
}

MODEL_CATALOG: dict[str, list[dict[str, str]]] = {
    "groq": [
        {"id": "llama-3.3-70b-versatile", "label": "Llama 3.3 70B"},
        {"id": "llama3-70b-8192", "label": "Llama 3 70B"},
        {"id": "mixtral-8x7b-32768", "label": "Mixtral 8x7B"},
    ],
    "openai": [
        {"id": "gpt-4o-mini", "label": "GPT-4o Mini"},
        {"id": "gpt-4o", "label": "GPT-4o"},
    ],
    "ollama": [
        {"id": "llama3.2", "label": "Llama 3.2"},
        {"id": "mistral", "label": "Mistral"},
        {"id": "gemma2", "label": "Gemma 2"},
    ],
}


def _default_model_for_provider(provider: str) -> str:
    settings = get_settings()
    defaults = {
        "groq": settings.groq_model,
        "openai": settings.openai_model,
        "ollama": settings.ollama_model,
    }
    if provider not in defaults:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return defaults[provider]


def resolve_llm_selection(
    provider: str | None = None,
    model_name: str | None = None,
) -> tuple[str, str]:
    settings = get_settings()
    resolved_provider = (provider or settings.llm_provider).lower()
    resolved_model = model_name or _default_model_for_provider(resolved_provider)
    return resolved_provider, resolved_model


def _provider_is_configured(provider: str) -> bool:
    settings = get_settings()
    if provider == "groq":
        return bool(settings.groq_api_key)
    if provider == "openai":
        return bool(settings.openai_api_key)
    if provider == "ollama":
        return True
    return False


def list_available_models() -> dict:
    settings = get_settings()
    default_provider, default_model = resolve_llm_selection()

    providers = []
    for provider_id, label in PROVIDER_LABELS.items():
        if not _provider_is_configured(provider_id):
            continue
        providers.append(
            {
                "id": provider_id,
                "label": label,
                "default_model": _default_model_for_provider(provider_id),
                "models": MODEL_CATALOG[provider_id],
            }
        )

    return {
        "default_provider": default_provider,
        "default_model": default_model,
        "providers": providers,
    }


def _build_llm(provider: str, model_name: str) -> BaseChatModel:
    settings = get_settings()

    if provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("Groq is not configured — set GROQ_API_KEY in .env")
        return ChatGroq(
            api_key=settings.groq_api_key,
            model_name=model_name,
            temperature=0.2,
            max_tokens=1024,
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI is not configured — set OPENAI_API_KEY in .env")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=model_name,
            temperature=0.2,
            max_tokens=1024,
        )

    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model_name,
            temperature=0.2,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


@lru_cache(maxsize=16)
def get_llm(provider: str | None = None, model_name: str | None = None) -> BaseChatModel:
    resolved_provider, resolved_model = resolve_llm_selection(provider, model_name)
    if not _provider_is_configured(resolved_provider):
        raise ValueError(
            f"LLM provider '{resolved_provider}' is not configured on the server"
        )
    return _build_llm(resolved_provider, resolved_model)
