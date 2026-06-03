"""
app/graph/pipeline.py
Builds and compiles the LangGraph StateGraph.

Graph topology
--------------

  START  →  retrieve_node  →  generate_node  →  format_node  →  END

Each node receives the full QAState, mutates its own fields, and passes
the merged state forward.
"""
from __future__ import annotations

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import format_node, generate_node, retrieve_node
from app.graph.state import QAState


@lru_cache(maxsize=1)
def get_pipeline():
    """
    Compile the LangGraph pipeline once and cache it for the process lifetime.
    Returns a CompiledGraph that exposes an `.invoke(state)` method.
    """
    builder = StateGraph(QAState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_node("format", format_node)

    # ── Wire edges ────────────────────────────────────────────────────────────
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", "format")
    builder.add_edge("format", END)

    return builder.compile()


def run_qa_pipeline(
    question: str,
    top_k: int = 4,
    session_id: str | None = None,
) -> dict:
    """
    Convenience wrapper that invokes the pipeline and returns
    the `structured_response` dict from the final state.
    """
    pipeline = get_pipeline()
    initial_state: QAState = {
        "question": question,
        "top_k": top_k,
        "session_id": session_id,
    }
    final_state: QAState = pipeline.invoke(initial_state)
    return final_state["structured_response"]
