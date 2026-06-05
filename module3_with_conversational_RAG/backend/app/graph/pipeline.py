"""
app/graph/pipeline.py
Convenience wrapper around the multi-turn RAG LangGraph.
"""
from __future__ import annotations

import uuid

from app.graph.rag_graph import get_compiled_rag_graph


async def run_qa_pipeline(
    question: str,
    top_k: int = 4,
    session_id: str | None = None,
) -> dict:
    """
    Invoke the RAG graph and return a dict compatible with AskResponse.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    rag_graph = get_compiled_rag_graph()
    final_state = await rag_graph.ainvoke({
        "session_id": session_id,
        "question": question,
        "messages": [],
        "context": "",
        "answer": "",
    })

    return {
        "question": question,
        "answer": final_state["answer"],
        "sources": [],
        "session_id": session_id,
    }
