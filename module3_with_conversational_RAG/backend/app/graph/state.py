# graph/state.py
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class RAGState(TypedDict):
    session_id: str
    question: str
    llm_provider: str
    model_name: str
    messages: Annotated[list, add_messages]   # LangGraph manages appending
    context: str                               # Retrieved from Qdrant
    answer: str
