# routes/chat.py
# Chat and history endpoints.
# POST /chat handles both normal chat and RAG based on pdf_id presence.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.chat import MessageRequest, MessageResponse, HistoryResponse
from app.services.chat_service import handle_message
from app.services.history_service import get_history
from app.db.database import get_db

router = APIRouter()

@router.post("/chat", response_model=MessageResponse)
def chat(request: MessageRequest, db: Session = Depends(get_db)):
    # Pass pdf_id to service — if present triggers RAG, otherwise normal chat
    reply, mode = handle_message(
        session_id=request.session_id,
        user_message=request.message,
        db=db,
        pdf_id=request.pdf_id
    )
    return MessageResponse(reply=reply, session_id=request.session_id, mode=mode)

@router.get("/history/{session_id}", response_model=HistoryResponse)
def history(session_id: str, db: Session = Depends(get_db)):
    # Return full chat history for a session
    messages = get_history(session_id, db)
    return HistoryResponse(session_id=session_id, messages=messages)