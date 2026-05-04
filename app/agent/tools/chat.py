from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session
from app.models.db import Conversation, Message, User


@tool
def get_recent_chat_messages(project_id: str, limit: int, config: RunnableConfig) -> str:
    """
    Fetches the most recent human chat messages for a project.
    Returns sender name, content, and timestamp in chronological order.
    Use this when the user asks to summarize the chat, find decisions,
    or recap what was discussed. Set limit between 10 and 100.
    """
    db: Session = config["configurable"]["db"]
    conversation = (
        db.query(Conversation)
        .filter(Conversation.projectId == project_id)
        .first()
    )
    if not conversation:
        return "No chat conversation found for this project."

    safe_limit = min(limit or 30, 100)  # Never fetch more than 100

    messages = (
        db.query(Message, User)
        .join(User, Message.senderId == User.id)
        .filter(
            Message.conversationId == conversation.id,
            Message.messageType == "TEXT",  # Skip AI/SYSTEM messages
        )
        .order_by(Message.createdAt.desc())
        .limit(safe_limit)
        .all()
    )

    if not messages:
        return "No messages found in this project's chat."

    messages = list(reversed(messages))  # Restore chronological order
    lines = [
        f"[{msg.createdAt.strftime('%Y-%m-%d %H:%M')}] {user.name}: {msg.content}"
        for msg, user in messages
    ]
    return "\n".join(lines)
