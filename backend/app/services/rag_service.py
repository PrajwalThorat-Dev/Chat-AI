# rag_service.py
# RAG pipeline using ChromaDB only — no PostgreSQL for chunk retrieval.
# search children → get parent_ids → fetch parent text from ChromaDB → LLaMA

from app.vector.chroma_store import search_chunks, fetch_parent_texts
from app.llm.ollama_llm import OllamaLLM
from app.services.history_service import save_message
from sqlalchemy.orm import Session

llm = OllamaLLM()

def build_rag_prompt(context_chunks: list[str], question: str) -> str:
    # Build strict prompt — LLaMA only answers from context
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

    # Step 1: search child vectors
    matched_children = search_chunks(query=question, pdf_id=pdf_id, top_k=3)

    print(f"DEBUG matched_children: {matched_children}")   # temporary log

    if not matched_children:
        return "No embeddings found for this document. Please delete and re-upload the PDF."

    # Step 2: get unique parent_ids
    parent_ids = list({
        child["parent_id"]
        for child in matched_children
        if child.get("parent_id")
    })

    # Step 3: fetch parent texts from ChromaDB
    context_chunks = fetch_parent_texts(parent_ids)


    if not context_chunks:
        return "Could not retrieve document context. Please try again."

    # Step 4: build prompt and call LLaMA
    prompt = build_rag_prompt(context_chunks, question)


    messages = [{"role": "user", "content": prompt}]
    answer = llm.generate(messages)


    return answer