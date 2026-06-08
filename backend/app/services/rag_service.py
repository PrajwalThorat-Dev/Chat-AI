# rag_service.py
# Core RAG pipeline: search ChromaDB → fetch context from PostgreSQL → call LLaMA.
# This is the main intelligence layer for PDF question answering.

from sqlalchemy.orm import Session
from app.vector.chroma_store import search_chunks
from app.db.models import DocumentChunk
from app.llm.ollama_llm import OllamaLLM

# Reuse the same LLM instance
llm = OllamaLLM()

def get_parent_chunks(parent_ids: list[str], db: Session) -> list[str]:
    # Fetch full parent chunk text from PostgreSQL using parent_ids.
    # Parent chunks have more context than child chunks.
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.id.in_(parent_ids),
        DocumentChunk.chunk_type == "parent"
    ).all()
    return [chunk.content for chunk in chunks]

def build_rag_prompt(context_chunks: list[str], question: str) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    return f"""You are a document assistant. You ONLY answer using the context below.
You must NEVER use outside knowledge or make assumptions.
If the answer is not explicitly in the context, respond with exactly:
"This information is not available in the document."

Context:
{context}

Question: {question}

Answer (based strictly on the context above):"""

def answer_with_rag(
    question: str,
    pdf_id: str,
    session_id: str,
    db: Session
) -> str:
    # Full RAG pipeline for one question.

    # Step 1: Search ChromaDB for relevant child chunks
    matched_children = search_chunks(
        query=question,
        pdf_id=pdf_id,
        top_k=3
    )

    if not matched_children:
        return "I could not find any relevant content in the document for your question."

    # Step 2: Get unique parent_ids from matched child chunks
    parent_ids = list({
        child["parent_id"]
        for child in matched_children
        if child.get("parent_id")
    })

    # Step 3: Fetch parent chunk text from PostgreSQL
    context_chunks = get_parent_chunks(parent_ids, db)

    if not context_chunks:
        return "I found relevant sections but could not retrieve the content. Please try again."

    # Step 4: Build prompt with context and question
    prompt = build_rag_prompt(context_chunks, question)

    # Step 5: Send to LLaMA and get answer
    messages = [{"role": "user", "content": prompt}]
    answer = llm.generate(messages)

    return answer