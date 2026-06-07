# pdf_service.py
# Handles PDF text extraction and parent-child chunking.
# Parent chunks = large context sent to LLM.
# Child chunks = small pieces used for embedding and searching.

import uuid
import fitz                                        # pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk

# Parent splitter — larger chunks, sent to LLM for context
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

# Child splitter — smaller chunks, used for embedding and search
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    # Open PDF from bytes and extract text page by page
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if text.strip():                           # skip empty pages
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
    # Extract text, create parent-child chunks, save all to PostgreSQL
    pages = extract_text_from_pdf(file_bytes)
    full_text = "\n".join([p["text"] for p in pages])

    # Create parent chunks from full text
    parent_texts = parent_splitter.split_text(full_text)

    total_children = 0

    for i, parent_text in enumerate(parent_texts):
        parent_id = str(uuid.uuid4())

        # Save parent chunk to DB
        parent_chunk = DocumentChunk(
            id=parent_id,
            pdf_id=pdf_id,
            filename=filename,
            chunk_index=i,
            chunk_type="parent",
            parent_id=None,                        # parents have no parent
            content=parent_text,
            page_number=None
        )
        db.add(parent_chunk)

        # Split parent into child chunks
        child_texts = child_splitter.split_text(parent_text)

        for j, child_text in enumerate(child_texts):
            child_chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                pdf_id=pdf_id,
                filename=filename,
                chunk_index=j,
                chunk_type="child",
                parent_id=parent_id,               # points back to parent
                content=child_text,
                page_number=None
            )
            db.add(child_chunk)
            total_children += 1

    db.commit()
    return total_children                          # return count for confirmation