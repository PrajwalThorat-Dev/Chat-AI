# upload.py
# Handles PDF file upload endpoint.
# Receives the file, triggers chunking, returns confirmation.

import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pdf_service import chunk_and_save

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file bytes
    file_bytes = await file.read()

    # Generate unique ID for this PDF
    pdf_id = str(uuid.uuid4())

    # Chunk and save to PostgreSQL
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