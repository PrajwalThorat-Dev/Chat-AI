# models.py
# Defines all database tables as SQLAlchemy ORM classes.
# ChatMessage stores chat history, DocumentChunk stores PDF chunks.

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.sql import func
from app.db.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)
    pdf_id = Column(String, nullable=False, index=True)   # which PDF this belongs to
    filename = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)          # position in document
    chunk_type = Column(String, nullable=False)            # "parent" or "child"
    parent_id = Column(String, nullable=True)              # child chunks point to their parent
    content = Column(Text, nullable=False)                 # actual text stored in PG
    page_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())