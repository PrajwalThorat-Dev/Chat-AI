# rag_service.py
# RAG pipeline using LangChain PromptTemplate.
# search children → fetch parent text → fill prompt → call LLaMA

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from app.vector.chroma_store import search_chunks, fetch_parent_texts
from app.llm.ollama_llm import OllamaLLM

llm = OllamaLLM()

# LangChain PromptTemplate — reusable and cleanly separated from logic
rag_prompt = ChatPromptTemplate.from_template("""
You are a document assistant. Answer using only the context below.
Do not use outside knowledge or make assumptions.
If the answer cannot be found in the context, respond with exactly:
"This information is not available in the document."
Use the context to answer the question clearly and concisely.

Context:
{context}

Question: {question}

Answer (based strictly on the context above):
""")

def build_rag_prompt(context_chunks: list[str], question: str) -> str:
    # Fill the LangChain prompt template with context and question
    context = "\n\n---\n\n".join(context_chunks)
    filled = rag_prompt.format_messages(
        context=context,
        question=question
    )
    # Extract text content from the formatted message
    return filled[0].content

def answer_with_rag(
    question: str,
    pdf_id: str,
    session_id: str,
    db: Session
) -> str:
    # Full RAG pipeline

    # Step 1: search child vectors
    matched_children = search_chunks(query=question, pdf_id=pdf_id, top_k=5)

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

    # Step 4: fill prompt template and call LLaMA
    prompt = build_rag_prompt(context_chunks, question)
    messages = [{"role": "user", "content": prompt}]
    answer = llm.generate(messages)

    return answer