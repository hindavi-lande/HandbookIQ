from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ChatSession


async def load_history(session_id: str, db: AsyncSession) -> list:
    """Load past messages for a session, ordered oldest first."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.session_id == session_id)
        .order_by(ChatSession.created_at.asc())
    )
    messages = []
    for row in result.scalars().all():
        if row.role == "human":
            messages.append(HumanMessage(content=row.content))
        else:
            messages.append(AIMessage(content=row.content))
    return messages


async def save_turn(session_id: str, question: str, answer: str, db: AsyncSession) -> None:
    """Persist one Q&A turn."""
    db.add_all(
        [
            ChatSession(session_id=session_id, role="human", content=question),
            ChatSession(session_id=session_id, role="assistant", content=answer),
        ]
    )
