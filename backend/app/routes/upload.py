# upload.py
# PDF upload, listing, and deletion endpoints.
# Uses ChromaDB only — no PostgreSQL for document chunks.

import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pdf_service import chunk_and_save
from app.vector.chroma_store import delete_pdf_from_chroma, get_uploaded_pdfs
from app.services.rag_service import answer_with_file


router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_bytes = await file.read()
    pdf_id = str(uuid.uuid4())

    # No db passed to chunk_and_save anymore
    total_chunks = chunk_and_save(
        pdf_id=pdf_id,
        filename=file.filename,
        file_bytes=file_bytes
    )

    return {
        "pdf_id": pdf_id,
        "filename": file.filename,
        "total_child_chunks": total_chunks,
        "message": "PDF uploaded and chunked successfully"
    }

@router.get("/pdfs")
def list_pdfs():
    # Fetch PDF list from ChromaDB instead of PostgreSQL
    pdfs = get_uploaded_pdfs()
    return {"pdfs": pdfs}

@router.delete("/pdfs/{pdf_id}")
def delete_pdf(pdf_id: str):
    # Delete all entries for this pdf_id from ChromaDB
    delete_pdf_from_chroma(pdf_id)
    return {"message": f"PDF {pdf_id} deleted successfully"}


@router.get("/debug/all-pdfs")
def debug_all_pdfs():
    from app.vector.chroma_store import collection
    results = collection.get(include=["metadatas"])
    pdf_ids = list({m["pdf_id"] for m in results["metadatas"]})
    return {"pdf_ids": pdf_ids, "total_entries": len(results["ids"])}

@router.post("/read-file")
async def read_file(
    file: UploadFile = File(...),
):
    file_bytes = await file.read()

    answer = answer_with_file(
        question="",
        filename=file.filename,
        file_bytes=file_bytes
    )

    return {
        "filename": file.filename,
        "answer": answer,
        "mode": "direct_read"
    }