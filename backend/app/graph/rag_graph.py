# graph/rag_graph.py
from __future__ import annotations

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.postgres import AsyncSessionLocal
from app.graph.nodes import (
    generate_node,
    load_history_node,
    retrieve_node,
    save_history_node,
)
from app.graph.state import RAGState

_compiled_graph = None


def build_rag_graph(llm, retriever, session_factory: async_sessionmaker[AsyncSession]):
    graph = StateGraph(RAGState)

    async def load_history(state: RAGState) -> dict:
        async with session_factory() as session:
            return await load_history_node(state, session)

    async def save_history(state: RAGState) -> dict:
        async with session_factory() as session:
            try:
                result = await save_history_node(state, session)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    async def retrieve(state: RAGState) -> dict:
        return await retrieve_node(state, retriever, llm)

    async def generate(state: RAGState) -> dict:
        return await generate_node(state, llm)

    graph.add_node("load_history", load_history)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_node("save_history", save_history)

    graph.set_entry_point("load_history")
    graph.add_edge("load_history", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "save_history")
    graph.add_edge("save_history", END)

    return graph.compile()


def init_rag_graph() -> None:
    global _compiled_graph
    from app.services.llm import get_llm
    from app.services.rag_retriever import get_retriever

    _compiled_graph = build_rag_graph(get_llm(), get_retriever(), AsyncSessionLocal)


def get_compiled_rag_graph():
    if _compiled_graph is None:
        raise RuntimeError("RAG graph not initialised — call init_rag_graph() on startup")
    return _compiled_graph
