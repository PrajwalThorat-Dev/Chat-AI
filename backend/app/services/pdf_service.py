# pdf_service.py
# Handles PDF text extraction and parent-child chunking.
# Uses LangChain PyMuPDFLoader for extraction with automatic page metadata.
# Saves parent text and child vectors to ChromaDB only.

import uuid
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.vector.chroma_store import add_parent_entry, add_child_entries
import tempfile
import os

# Larger chunks for better context — tuned for books
parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=50
)

# Smaller chunks for precise embedding and search
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

def extract_text_from_pdf(file_bytes: bytes) -> list:
    # LangChain PyMuPDFLoader requires a file path not bytes.
    # Write to a temp file, load, then delete.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loader = PyMuPDFLoader(tmp_path)
        documents = loader.load()          # returns list of Document objects
    finally:
        os.unlink(tmp_path)                # always delete temp file

    return documents

def chunk_and_save(
    pdf_id: str,
    filename: str,
    file_bytes: bytes
) -> int:
    # Full pipeline: extract → chunk → save to ChromaDB only.

    documents = extract_text_from_pdf(file_bytes)

    # Each document is one page with metadata like page_number, source
    # Combine all page texts for parent chunking
    full_text = "\n".join([doc.page_content for doc in documents])

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

        # Create child chunks and queue for batch embedding
        child_texts = child_splitter.split_text(parent_text)

        for j, child_text in enumerate(child_texts):
            child_chunks_for_chroma.append({
                "id": str(uuid.uuid4()),
                "content": child_text,
                "pdf_id": pdf_id,
                "parent_id": parent_id,
                "filename": filename
            })
            total_children += 1

    # Batch embed all children and store in ChromaDB
    add_child_entries(child_chunks_for_chroma)

    return total_children