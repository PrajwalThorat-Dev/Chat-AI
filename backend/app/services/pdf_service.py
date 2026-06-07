# pdf_service.py
# Handles PDF text extraction, parent-child chunking,
# saving chunk text to PostgreSQL, and embeddings to ChromaDB.

import uuid
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk
from app.vector.chroma_store import add_chunks_to_chroma

# Larger chunks for better context — tuned for books
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=50
)

child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    # Open PDF from bytes and extract text page by page
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if text.strip():
            pages.append({
                "page_number": page_num + 1,
                "text": text
            })
    return pages

def chunk_and_save(
    pdf_id: str,
    filename: str,
    file_bytes: bytes,
    db: Session
) -> int:
    # Full pipeline: extract → chunk → save to PG → embed in ChromaDB
    pages = extract_text_from_pdf(file_bytes)
    full_text = "\n".join([p["text"] for p in pages])

    parent_texts = parent_splitter.split_text(full_text)

    # Collect child chunks for batch embedding at the end
    child_chunks_for_chroma = []
    total_children = 0

    for i, parent_text in enumerate(parent_texts):
        parent_id = str(uuid.uuid4())

        # Save parent chunk text to PostgreSQL
        parent_chunk = DocumentChunk(
            id=parent_id,
            pdf_id=pdf_id,
            filename=filename,
            chunk_index=i,
            chunk_type="parent",
            parent_id=None,
            content=parent_text,
            page_number=None
        )
        db.add(parent_chunk)

        # Create and save child chunks
        child_texts = child_splitter.split_text(parent_text)

        for j, child_text in enumerate(child_texts):
            child_id = str(uuid.uuid4())

            # Save child chunk text to PostgreSQL
            child_chunk = DocumentChunk(
                id=child_id,
                pdf_id=pdf_id,
                filename=filename,
                chunk_index=j,
                chunk_type="child",
                parent_id=parent_id,
                content=child_text,
                page_number=None
            )
            db.add(child_chunk)

            # Queue for ChromaDB embedding
            child_chunks_for_chroma.append({
                "id": child_id,
                "content": child_text,
                "pdf_id": pdf_id,
                "parent_id": parent_id,
                "filename": filename
            })
            total_children += 1

    # Commit all chunks to PostgreSQL first
    db.commit()

    # Then embed all child chunks and store in ChromaDB
    add_chunks_to_chroma(child_chunks_for_chroma)

    return total_children