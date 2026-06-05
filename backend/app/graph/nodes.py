# graph/nodes.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.state import RAGState
from app.memory.postgres_history import load_history, save_turn

# Node 1 — Load history from Postgres into state
async def load_history_node(state: RAGState, db: AsyncSession) -> dict:
    history = await load_history(state["session_id"], db)
    return {"messages": history}   # LangGraph appends via add_messages

# Node 2 — Retrieve from Qdrant
async def retrieve_node(state: RAGState, retriever) -> dict:
    docs = await retriever.ainvoke(state["question"])
    context = "\n\n".join(d.page_content for d in docs)
    return {"context": context}

# NLLM call with full history + context
async def generate_node(state: RAGState, llm) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant. Use the context below to answer.
If unsure, say you don't know.

Context:
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
