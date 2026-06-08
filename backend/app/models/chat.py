# models/chat.py
# Pydantic models defining API request and response shapes.
# MessageRequest now optionally accepts a pdf_id for RAG queries.

from pydantic import BaseModel
from typing import List, Optional

class MessageRequest(BaseModel):
    session_id: str
    message: str
    pdf_id: Optional[str] = None       # if provided, RAG mode is used

class MessageItem(BaseModel):
    content: str

class MessageResponse(BaseModel):
    reply: str
    session_id: str
    mode: str = "chat"                 # "chat" or "rag" — tells frontend which mode was used

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]