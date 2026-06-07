# routes/chat.py
# Defines API endpoints for chat and history.
# Receives requests, passes them to the service layer, returns responses.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.chat import MessageRequest, MessageResponse, HistoryResponse
from app.services.chat_service import handle_message
from app.services.history_service import get_history
from app.db.database import get_db

router = APIRouter()

@router.post("/chat", response_model=MessageResponse)
def chat(request: MessageRequest, db: Session = Depends(get_db)):
    # Pass db session to service layer
    reply = handle_message(request.session_id, request.message, db)
    return MessageResponse(reply=reply, session_id=request.session_id)

@router.get("/history/{session_id}", response_model=HistoryResponse)
def history(session_id: str, db: Session = Depends(get_db)):
    # Fetch all messages for this session from DB
    messages = get_history(session_id, db)
    return HistoryResponse(session_id=session_id, messages=messages)