# graph/nodes.py
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.state import RAGState
from app.memory.postgres_history import load_history, save_turn

logger = logging.getLogger(__name__)

# Node 1 — Load history from Postgres into state
async def load_history_node(state: RAGState, db: AsyncSession) -> dict:
    history = await load_history(state["session_id"], db)
    if history:
        logger.info(
            "Loaded chat history for session_id=%s (%d messages)",
            state["session_id"],
            len(history),
        )
    else:
        logger.info(
            "Loaded chat history for session_id=%s: [] (new or unknown session)",
            state["session_id"],
        )
    return {"messages": history}   # LangGraph appends via add_messages

# Node 2 — Retrieve from Qdrant
async def retrieve_node(state: RAGState, retriever, llm) -> dict:
    """
    Rewrite follow-up questions into standalone queries using chat history,
    then retrieve documents for the rewritten query.
    """
    user_query = state["question"]
    chat_history = state.get("messages", []) or []

    logger.info("User query (session_id=%s): %s", state["session_id"], user_query)
    logger.info(
        "Chat history (session_id=%s): %s",
        state["session_id"],
        [
            {
                "role": m.type,
                "content": (m.content[:200] + "…") if len(m.content) > 200 else m.content,
            }
            for m in chat_history
        ],
    )

    standalone_query = user_query
    if chat_history:
        rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Rewrite the user's latest question into a standalone question that can be used for retrieval. "
                    "Use the chat history for context. Return ONLY the standalone question.",
                ),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        rewrite_chain = rewrite_prompt | llm | StrOutputParser()
        standalone_query = (
            await rewrite_chain.ainvoke({"chat_history": chat_history, "input": user_query})
        ).strip()

    logger.info(
        "Rewritten standalone query (session_id=%s): %s",
        state["session_id"],
        standalone_query,
    )

    # IMPORTANT: Qdrant retrieval must use the rewritten standalone query, not the raw user query.
    docs = await retriever.ainvoke(standalone_query)
    logger.info(
        "Retrieved %d documents (session_id=%s): %s",
        len(docs),
        state["session_id"],
        [
            {
                "chunk_id": d.metadata.get("chunk_id"),
                "source_file": d.metadata.get("source_file"),
                "score": d.metadata.get("score"),
                "excerpt": (d.page_content[:200] + "…") if len(d.page_content) > 200 else d.page_content,
            }
            for d in docs
        ],
    )
    context = "\n\n".join(d.page_content for d in docs)
    return {"context": context}

# NLLM call with full history + context
async def generate_node(state: RAGState, llm) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful company handbook assistant. Answer the user's question directly and conversationally using the handbook excerpts below.

Rules:
- Do not mention "context", "documents", "excerpts", or "according to the handbook" unless the user asks where the information came from.
- Do not start answers with phrases like "According to the context" or "Based on the provided information".
- If the excerpts do not contain enough information, say you don't know.

Handbook excerpts:
{context}"""),
        MessagesPlaceholder("messages"),   # ← history slots in here
        ("human", "{question}"),
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "context":   state["context"],
        "messages":  state["messages"],
        "question":  state["question"],
    })
    return {"answer": response.content}

# Node 4 — Persist turn back to Postgres
async def save_history_node(state: RAGState, db: AsyncSession) -> dict:
    await save_turn(
        state["session_id"],
        state["question"],
        state["answer"],
        db
    )
    # LangGraph requires every node to write at least one state key.
    return {"answer": state["answer"]}
