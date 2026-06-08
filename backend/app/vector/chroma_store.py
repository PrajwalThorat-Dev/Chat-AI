# chroma_store.py
# Manages ChromaDB vector store for storing and searching embeddings.
# Only child chunks are embedded and stored here.
# Parent chunk text is stored in PostgreSQL and fetched by parent_id.

import chromadb
import ollama

# Initialize ChromaDB with persistent storage so data survives restarts
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# Single collection for all document chunks
collection = chroma_client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"}   # cosine similarity for text search
)

def get_embedding(text: str) -> list[float]:
    # Generate embedding vector for a piece of text using Ollama
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

def add_chunks_to_chroma(chunks: list[dict]):
    # Store child chunk embeddings in ChromaDB.
    # Each chunk dict must have: id, content, pdf_id, parent_id, filename

    ids = []
    embeddings = []
    metadatas = []

    for chunk in chunks:
        # Generate embedding for this chunk's text
        embedding = get_embedding(chunk["content"])

        ids.append(chunk["id"])
        embeddings.append(embedding)

        # Store metadata for filtering later (no large text here)
        metadatas.append({
            "pdf_id": chunk["pdf_id"],
            "parent_id": chunk["parent_id"],
            "filename": chunk["filename"],
            "chunk_type": "child"
        })

    # Batch insert into ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )

def search_chunks(query: str, pdf_id: str, top_k: int = 3) -> list[dict]:
    # Search ChromaDB for most relevant child chunks.
    # Filters by pdf_id so results only come from the correct document.
    # Returns list of metadata dicts with parent_ids for PostgreSQL lookup.

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"pdf_id": pdf_id}        # metadata filter
    )

    # Return metadata list (contains parent_ids we need)
    if not results["metadatas"] or not results["metadatas"][0]:
        return []

    return results["metadatas"][0]

def delete_pdf_from_chroma(pdf_id: str):
    # Delete all embeddings for a specific pdf_id from ChromaDB
    results = collection.get(where={"pdf_id": pdf_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])

def get_all_pdf_ids() -> list[str]:
    # Return all unique pdf_ids currently stored in ChromaDB
    results = collection.get()
    pdf_ids = list({
        meta["pdf_id"]
        for meta in results["metadatas"]
        if meta.get("pdf_id")
    })
    return pdf_ids