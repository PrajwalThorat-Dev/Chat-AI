# chat_service.py
from sqlalchemy.orm import Session
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from app.llm.ollama_llm import OllamaLLM
from app.services.history_service import get_history, save_message
from app.services.rag_service import answer_with_rag

llm = OllamaLLM()

# Per-session history store
_history_store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    # Get or create chat history for a session
    if session_id not in _history_store:
        _history_store[session_id] = ChatMessageHistory()
    return _history_store[session_id]

def load_history_into_memory(session_id: str, db: Session):
    # Load existing DB history into LangChain memory on first use
    history_obj = get_session_history(session_id)

    # Only load if empty
    if len(history_obj.messages) == 0:
        history = get_history(session_id, db)
        for msg in history:
            if msg["role"] == "user":
                history_obj.add_message(HumanMessage(content=msg["content"]))
            else:
                history_obj.add_message(AIMessage(content=msg["content"]))

def handle_message(
    session_id: str,
    user_message: str,
    db: Session,
    pdf_id: str = None
) -> tuple[str, str]:

    # Save user message to PostgreSQL
    save_message(session_id, role="user", content=user_message, db=db)

    if pdf_id:
        # RAG mode
        reply = answer_with_rag(
            question=user_message,
            pdf_id=pdf_id,
            session_id=session_id,
            db=db
        )
        mode = "rag"
    else:
        # Normal chat with LangChain message history
        load_history_into_memory(session_id, db)
        history_obj = get_session_history(session_id)

        # Build messages list from history
        messages = []
        for msg in history_obj.messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            else:
                messages.append({"role": "assistant", "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": user_message})
        reply = llm.generate(messages)

        # Save to LangChain history
        history_obj.add_message(HumanMessage(content=user_message))
        history_obj.add_message(AIMessage(content=reply))
        mode = "chat"

    # Save reply to PostgreSQL
    save_message(session_id, role="assistant", content=reply, db=db)

    return reply, mode