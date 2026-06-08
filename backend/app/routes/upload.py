# upload.py
# Handles PDF file upload, listing, and deletion endpoints.
# Receives the file, triggers chunking, returns confirmation.

import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pdf_service import chunk_and_save
from app.services.history_service import delete_pdf_chunks, get_uploaded_pdfs
from app.vector.chroma_store import delete_pdf_from_chroma

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

    total_chunks = chunk_and_save(
        pdf_id=pdf_id,
        filename=file.filename,
        file_bytes=file_bytes,
        db=db
    )

    return {
        "pdf_id": pdf_id,
        "filename": file.filename,
        "total_child_chunks": total_chunks,
        "message": "PDF uploaded and chunked successfully"
    }

@router.get("/pdfs")
def list_pdfs(db: Session = Depends(get_db)):
    # List all uploaded PDFs
    pdfs = get_uploaded_pdfs(db)
    return {"pdfs": pdfs}

@router.delete("/pdfs/{pdf_id}")
def delete_pdf(pdf_id: str, db: Session = Depends(get_db)):
    # Delete a PDF's data from both PostgreSQL and ChromaDB
    delete_pdf_chunks(pdf_id, db)
    delete_pdf_from_chroma(pdf_id)
    return {"message": f"PDF {pdf_id} deleted successfully"}