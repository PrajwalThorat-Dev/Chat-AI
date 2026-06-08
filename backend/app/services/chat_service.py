# chat_service.py
# Routes the message to either normal chat or RAG pipeline.
# If pdf_id is provided, RAG is used. Otherwise normal LLM chat.

from sqlalchemy.orm import Session
from app.llm.ollama_llm import OllamaLLM
from app.services.history_service import get_history, save_message
from app.services.rag_service import answer_with_rag

llm = OllamaLLM()

def handle_message(
    session_id: str,
    user_message: str,
    db: Session,
    pdf_id: str = None             # optional — triggers RAG mode
) -> tuple[str, str]:
    # Returns (reply, mode) so route knows which mode was used

    # Save user message to DB regardless of mode
    save_message(session_id, role="user", content=user_message, db=db)

    if pdf_id:
        # RAG mode — answer from PDF context
        reply = answer_with_rag(
            question=user_message,
            pdf_id=pdf_id,
            session_id=session_id,
            db=db
        )
        mode = "rag"
    else:
        # Normal chat mode — use full conversation history
        history = get_history(session_id, db)
        messages = history + [{"role": "user", "content": user_message}]
        reply = llm.generate(messages)
        mode = "chat"

    # Save assistant reply to DB
    save_message(session_id, role="assistant", content=reply, db=db)

    return reply, mode