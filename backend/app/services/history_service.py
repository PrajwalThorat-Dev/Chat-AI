import uuid
from sqlalchemy.orm import Session
from app.db.models import ChatMessage
from app.db.models import ChatMessage, DocumentChunk

def get_history(session_id: str, db: Session):
    messages = db.query(ChatMessage)\
                 .filter(ChatMessage.session_id == session_id)\
                 .order_by(ChatMessage.created_at)\
                 .all()
    return [{"role": m.role, "content": m.content} for m in messages]

def save_message(session_id: str, role: str, content: str, db: Session):
    message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()

def delete_pdf_chunks(pdf_id: str, db: Session):
    # Delete all chunks for a pdf_id from PostgreSQL
    db.query(DocumentChunk)\
      .filter(DocumentChunk.pdf_id == pdf_id)\
      .delete()
    db.commit()

def get_uploaded_pdfs(db: Session) -> list[dict]:
    # Return list of unique PDFs uploaded so far
    chunks = db.query(
        DocumentChunk.pdf_id,
        DocumentChunk.filename
    ).filter(
        DocumentChunk.chunk_type == "parent"
    ).distinct().all()
    return [{"pdf_id": c.pdf_id, "filename": c.filename} for c in chunks]