# chat_service.py
# Routes messages to chat, RAG, or agent mode.
# Agent mode triggered when user message contains a file path.

import re
from sqlalchemy.orm import Session
from langchain_ollama import OllamaLLM as LangChainOllama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from app.services.history_service import get_history, save_message
from app.services.rag_service import answer_with_rag
from app.services.agent_service import answer_with_agent

llm = LangChainOllama(model="llama3.2:3b")

_history_store: dict[str, ChatMessageHistory] = {}

def has_file_path(message: str) -> bool:
    # Detect Windows or Unix file path in message
    windows_path = re.search(r'[A-Za-z]:\\[\w\\.\- ]+', message)
    unix_path = re.search(r'\/[\w\/.\-]+\.\w+', message)
    return bool(windows_path or unix_path)

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _history_store:
        _history_store[session_id] = ChatMessageHistory()
    return _history_store[session_id]

def load_history_into_memory(session_id: str, db: Session):
    history_obj = get_session_history(session_id)
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

    save_message(session_id, role="user", content=user_message, db=db)

    if pdf_id:
        # RAG mode — uploaded PDF
        reply = answer_with_rag(
            question=user_message,
            pdf_id=pdf_id,
            session_id=session_id,
            db=db
        )
        mode = "rag"

    elif has_file_path(user_message):
        # Agent mode — file path detected in message
        reply = answer_with_agent(question=user_message)
        mode = "rag"

    else:
        # Normal chat mode
        load_history_into_memory(session_id, db)
        history_obj = get_session_history(session_id)
        messages = []
        for msg in history_obj.messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            else:
                messages.append({"role": "assistant", "content": msg.content})
        messages.append({"role": "user", "content": user_message})
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        reply = llm.invoke(full_prompt)
        history_obj.add_message(HumanMessage(content=user_message))
        history_obj.add_message(AIMessage(content=reply))
        mode = "chat"

    save_message(session_id, role="assistant", content=reply, db=db)
    return reply, mode