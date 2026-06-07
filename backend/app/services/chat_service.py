# chat_service.py
# Core business logic for handling a chat message.
# Connects history, LLM, and storage together.

from sqlalchemy.orm import Session
from app.llm.ollama_llm import OllamaLLM                  # swapped from MockLLM
from app.services.history_service import get_history, save_message

# Single LLM instance reused across all requests
llm = OllamaLLM()

def handle_message(session_id: str, user_message: str, db: Session) -> str:
    # Fetch previous messages for this session
    history = get_history(session_id, db)

    # Save the user's message to DB
    save_message(session_id, role="user", content=user_message, db=db)

    # Build full message list: history + new user message
    messages = history + [{"role": "user", "content": user_message}]

    # Call LLM and get reply
    reply = llm.generate(messages)

    # Save assistant reply to DB
    save_message(session_id, role="assistant", content=reply, db=db)

    return reply