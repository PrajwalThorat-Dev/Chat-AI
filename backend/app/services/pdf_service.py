# pdf_service.py
# Handles PDF text extraction and parent-child chunking.
# Saves parent text and child vectors to ChromaDB only.
# No PostgreSQL dependency for document chunks.

import uuid
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.vector.chroma_store import add_parent_entry, add_child_entries

# Larger chunks for better context
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=50
)

# Smaller chunks for precise embedding and search
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    # Extract text from each page of the PDF
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
    file_bytes: bytes
) -> int:
    # Full pipeline: extract → chunk → save to ChromaDB only.
    # db parameter removed — no PostgreSQL writes for chunks.

    pages = extract_text_from_pdf(file_bytes)
    full_text = "\n".join([p["text"] for p in pages])

    parent_texts = parent_splitter.split_text(full_text)

    child_chunks_for_chroma = []
    total_children = 0

    for i, parent_text in enumerate(parent_texts):
        parent_id = str(uuid.uuid4())

        # Save parent text to ChromaDB document field
        add_parent_entry(
            parent_id=parent_id,
            pdf_id=pdf_id,
            filename=filename,
            parent_text=parent_text
        )

        # Create child chunks and queue for embedding
        child_texts = child_splitter.split_text(parent_text)

        for j, child_text in enumerate(child_texts):
            child_chunks_for_chroma.append({
                "id": str(uuid.uuid4()),
                "content": child_text,         # used for embedding then discarded
                "pdf_id": pdf_id,
                "parent_id": parent_id,
                "filename": filename
            })
            total_children += 1

    # Embed all children and store vectors in ChromaDB
    add_child_entries(child_chunks_for_chroma)

    return total_children