"""
app/routers/models.py
GET /api/models — list configured LLM providers and model options.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import ModelsResponse
from app.services.llm import list_available_models

router = APIRouter(prefix="/api", tags=["Models"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List available LLM providers and models",
)
def get_models() -> ModelsResponse:
    return ModelsResponse(**list_available_models())
