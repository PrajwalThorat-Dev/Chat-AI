# history_service.py
# Manages chat message history in PostgreSQL.
# PDF chunk functions removed — now handled by chroma_store.py.

import uuid
from sqlalchemy.orm import Session
from app.db.models import ChatMessage

def get_history(session_id: str, db: Session):
    # Fetch all messages for a session ordered by time
    messages = db.query(ChatMessage)\
                 .filter(ChatMessage.session_id == session_id)\
                 .order_by(ChatMessage.created_at)\
                 .all()
    return [{"role": m.role, "content": m.content} for m in messages]

def save_message(session_id: str, role: str, content: str, db: Session):
    # Save a single message to PostgreSQL
    message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()