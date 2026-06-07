from pydantic import BaseModel
from typing import List

class MessageRequest(BaseModel):
    session_id: str
    message: str

class MessageItem(BaseModel):
    content: str

class MessageResponse(BaseModel):
    reply: str
    session_id: str

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]