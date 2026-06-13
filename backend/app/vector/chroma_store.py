# chroma_store.py
# Manages all ChromaDB operations using LangChain Chroma wrapper.
# Parent text stored in document field, child vectors for search.

import uuid
import chromadb
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings

# LangChain embedding model
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# Persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# LangChain Chroma wrapper — handles embedding and storage together
vectorstore = Chroma(
    client=chroma_client,
    collection_name="document_chunks",
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

# Raw collection for manual parent/child operations
collection = chroma_client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"}
)

# Dummy vector for parent entries
DUMMY_VECTOR = [0.0] * 768

def add_parent_entry(parent_id: str, pdf_id: str, filename: str, parent_text: str):
    # Store parent text in ChromaDB document field with dummy vector
    collection.add(
        ids=[parent_id],
        embeddings=[DUMMY_VECTOR],
        documents=[parent_text],
        metadatas=[{
            "pdf_id": pdf_id,
            "chunk_type": "parent",
            "filename": filename
        }]
    )

def add_child_entries(chunks: list[dict]):
    # Batch embed all child chunks and store in ChromaDB
    if not chunks:
        return

    ids = []
    metadatas = []
    documents = []
    texts_to_embed = []

    for chunk in chunks:
        ids.append(chunk["id"])
        documents.append("")
        metadatas.append({
            "pdf_id": chunk["pdf_id"],
            "chunk_type": "child",
            "parent_id": chunk["parent_id"],
            "filename": chunk["filename"]
        })
        texts_to_embed.append(chunk["content"])

    # Single batch call for all embeddings
    embeddings = get_embeddings_batch(texts_to_embed)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
def fetch_parent_texts(parent_ids: list[str]) -> list[str]:
    # Fetch parent text from ChromaDB by parent_ids
    if not parent_ids:
        return []

    results = collection.get(
        ids=parent_ids,
        include=["documents", "metadatas"]
    )

    texts = []
    for i, meta in enumerate(results["metadatas"]):
        if meta.get("chunk_type") == "parent":
            doc = results["documents"][i]
            if doc:
                texts.append(doc)

    return texts

def get_uploaded_pdfs() -> list[dict]:
    # Return unique PDFs from parent entries
    results = collection.get(
        where={"chunk_type": {"$eq": "parent"}},
        include=["metadatas"]
    )

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
    # Delete all entries for a pdf_id
    results = collection.get(
        where={"pdf_id": {"$eq": pdf_id}}
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])