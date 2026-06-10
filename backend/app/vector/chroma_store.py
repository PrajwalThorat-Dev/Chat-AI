# chroma_store.py
# Manages all ChromaDB operations.
# Stores parent text in document field and child vectors for search.
# No PostgreSQL dependency for document chunks.

import chromadb
import ollama

# Persistent ChromaDB client — data survives server restarts
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# Single collection for both parent and child entries
collection = chroma_client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"}
)

# Dummy vector for parent entries — must match nomic-embed-text dimensions
DUMMY_VECTOR = [0.0] * 768

def get_embedding(text: str) -> list[float]:
    # Generate embedding vector for a piece of text using Ollama
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

def add_parent_entry(
    parent_id: str,
    pdf_id: str,
    filename: str,
    parent_text: str
):
    # Store parent chunk text in ChromaDB document field.
    # Uses dummy vector since parents are never searched directly.
    collection.add(
        ids=[parent_id],
        embeddings=[DUMMY_VECTOR],
        documents=[parent_text],           # full parent text stored here
        metadatas=[{
            "pdf_id": pdf_id,
            "chunk_type": "parent",
            "filename": filename
        }]
    )

def add_child_entries(chunks: list[dict]):
    # Store child chunk embeddings in ChromaDB.
    # Child text is NOT stored — only the vector and parent_id mapping.
    # Each chunk dict must have: id, content, pdf_id, parent_id, filename

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for chunk in chunks:
        # Generate real embedding from child text
        embedding = get_embedding(chunk["content"])

        ids.append(chunk["id"])
        embeddings.append(embedding)
        documents.append("")               # child text discarded after embedding
        metadatas.append({
            "pdf_id": chunk["pdf_id"],
            "chunk_type": "child",
            "parent_id": chunk["parent_id"],
            "filename": chunk["filename"]
        })

    # Batch insert all children
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

def search_chunks(query: str, pdf_id: str, top_k: int = 3) -> list[dict]:
    # Search for relevant child chunks using vector similarity.
    # Filters by pdf_id and chunk_type=child.

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "$and": [
                {"pdf_id": {"$eq": pdf_id}},
                {"chunk_type": {"$eq": "child"}}
            ]
        },
        include=["metadatas", "distances"]
    )

    if not results["metadatas"] or not results["metadatas"][0]:
        return []

    return results["metadatas"][0]

def fetch_parent_texts(parent_ids: list[str]) -> list[str]:
    # Fetch parent text from ChromaDB document field by parent_ids.

    if not parent_ids:
        return []

    results = collection.get(
        ids=parent_ids,
        include=["documents", "metadatas"]
    )

    # Filter only parent entries and return their document text
    texts = []
    for i, meta in enumerate(results["metadatas"]):
        if meta.get("chunk_type") == "parent":
            doc = results["documents"][i]
            if doc:                            # skip empty documents
                texts.append(doc)

    return texts

def get_uploaded_pdfs() -> list[dict]:
    # Return list of unique PDFs by fetching parent entries.
    # Replaces the old PostgreSQL get_uploaded_pdfs() function.

    results = collection.get(
        where={"chunk_type": {"$eq": "parent"}},
        include=["metadatas"]
    )

    # Deduplicate by pdf_id
    seen = set()
    pdfs = []
    for meta in results["metadatas"]:
        if meta["pdf_id"] not in seen:
            seen.add(meta["pdf_id"])
            pdfs.append({
                "pdf_id": meta["pdf_id"],
                "filename": meta["filename"]
            })

    return pdfs

def delete_pdf_from_chroma(pdf_id: str):
    # Delete all entries (both parent and child) for a pdf_id.

    results = collection.get(
        where={"pdf_id": {"$eq": pdf_id}}
    )

    if results["ids"]:
        collection.delete(ids=results["ids"])