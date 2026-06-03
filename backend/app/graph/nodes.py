"""
app/graph/nodes.py
Three nodes that make up the Q&A pipeline:

  retrieve_node   – fetch semantically relevant chunks from Qdrant
  generate_node   – build a prompt and call Groq (via LangChain)
  format_node     – assemble the final structured response dict
"""
from __future__ import annotations

import logging
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

from app.config import get_settings
from app.graph.state import QAState
from app.services.retriever import retrieve

logger = logging.getLogger(__name__)
_settings = get_settings()

# ── Shared LLM instance (created once per process) ───────────────────────────
_llm = ChatGroq(
    api_key=_settings.groq_api_key,
    model_name=_settings.groq_model,
    temperature=0.2,
    max_tokens=1024,
)

# ── System prompt ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """\
You are a helpful HR assistant for a company handbook Q&A system.
Answer questions ONLY based on the provided context excerpts.
If the context does not contain enough information, say:
"I'm sorry, I couldn't find a clear answer in the handbook. Please contact HR directly."
Be concise, professional, and accurate.
Do NOT make up information.
"""


# ── Node 1: Retrieve ──────────────────────────────────────────────────────────

def retrieve_node(state: QAState) -> QAState:
    """Embed the question and fetch top-k chunks from Qdrant."""
    question = state["question"]
    top_k = state.get("top_k", 4)

    try:
        chunks = retrieve(question=question, top_k=top_k)
        return {**state, "retrieved_chunks": chunks, "error": None}
    except Exception as exc:
        logger.exception("retrieve_node failed")
        return {**state, "retrieved_chunks": [], "error": str(exc)}


# ── Node 2: Generate ──────────────────────────────────────────────────────────

def generate_node(state: QAState) -> QAState:
    """Build a RAG prompt and call the Groq LLM."""
    question = state["question"]
    chunks = state.get("retrieved_chunks", [])

    if state.get("error"):
        # Propagate upstream error – skip generation
        return {**state, "answer": "An error occurred during retrieval."}

    if not chunks:
        return {
            **state,
            "answer": (
                "I'm sorry, I couldn't find a clear answer in the handbook. "
                "Please contact HR directly."
            ),
        }

    # Build the context block from retrieved excerpts
    context_lines = []
    for i, chunk in enumerate(chunks, start=1):
        context_lines.append(
            f"[{i}] (source: {chunk.source_file}, score: {chunk.score})\n"
            f"{chunk.excerpt}"
        )
    context = "\n\n".join(context_lines)

    user_message = (
        f"Context from the company handbook:\n\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer (based only on the context above):"
    )

    try:
        response = _llm.invoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
        )
        answer = response.content.strip()
    except Exception as exc:
        logger.exception("generate_node LLM call failed")
        answer = f"LLM error: {exc}"

    return {**state, "answer": answer}


# ── Node 3: Format ────────────────────────────────────────────────────────────

def format_node(state: QAState) -> QAState:
    """Assemble the final dict that the API router will return as JSON."""
    structured = {
        "question": state["question"],
        "answer": state.get("answer", ""),
        "sources": [chunk.model_dump() for chunk in state.get("retrieved_chunks", [])],
        "session_id": state.get("session_id"),
        "created_at": datetime.utcnow().isoformat(),
    }
    return {**state, "structured_response": structured}
