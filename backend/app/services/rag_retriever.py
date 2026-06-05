"""
app/services/rag_retriever.py
LangChain retriever wrapper around Qdrant semantic search.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from app.services.retriever import retrieve


class HandbookRetriever(BaseRetriever):
    """Exposes Qdrant retrieval via retriever.ainvoke(question)."""

    top_k: int = Field(default=4, ge=1, le=10)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
    ) -> List[Document]:
        chunks = retrieve(question=query, top_k=self.top_k)
        return [
            Document(
                page_content=chunk.excerpt,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "source_file": chunk.source_file,
                    "score": chunk.score,
                },
            )
            for chunk in chunks
        ]

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun | None = None,
    ) -> List[Document]:
        return self._get_relevant_documents(query)


@lru_cache(maxsize=1)
def get_retriever(top_k: int = 4) -> HandbookRetriever:
    return HandbookRetriever(top_k=top_k)
