from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())