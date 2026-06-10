# upload.py
# PDF upload, listing, and deletion endpoints.
# Uses ChromaDB only — no PostgreSQL for document chunks.

import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.pdf_service import chunk_and_save
from app.vector.chroma_store import delete_pdf_from_chroma, get_uploaded_pdfs

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

@router.get("/debug/rag-full/{pdf_id}")
def debug_rag_full(pdf_id: str, q: str = "travel expense policies"):
    from app.vector.chroma_store import search_chunks, fetch_parent_texts, collection

    # Check total entries
    all_data = collection.get(where={"pdf_id": {"$eq": pdf_id}}, include=["metadatas", "documents"])
    parents = [i for i, m in enumerate(all_data["metadatas"]) if m["chunk_type"] == "parent"]
    children = [i for i, m in enumerate(all_data["metadatas"]) if m["chunk_type"] == "child"]

    # Check search
    matched = search_chunks(query=q, pdf_id=pdf_id, top_k=3)

    # Check parent fetch
    parent_ids = list({c["parent_id"] for c in matched if c.get("parent_id")})
    texts = fetch_parent_texts(parent_ids)

    # Check parent documents directly
    parent_docs = [all_data["documents"][i] for i in parents]

    return {
        "total_entries": len(all_data["ids"]),
        "parent_count": len(parents),
        "child_count": len(children),
        "parent_docs_preview": [d[:100] if d else "EMPTY" for d in parent_docs],
        "search_matched": len(matched),
        "parent_ids_found": parent_ids,
        "fetch_parent_texts_result": len(texts),
        "texts_preview": [t[:100] for t in texts] if texts else "EMPTY"
    }

@router.get("/debug/all-pdfs")
def debug_all_pdfs():
    from app.vector.chroma_store import collection
    results = collection.get(include=["metadatas"])
    pdf_ids = list({m["pdf_id"] for m in results["metadatas"]})
    return {"pdf_ids": pdf_ids, "total_entries": len(results["ids"])}