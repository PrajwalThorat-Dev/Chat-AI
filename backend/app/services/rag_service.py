# rag_service.py
# RAG pipeline using LangChain PromptTemplate.
# search children → fetch parent text → fill prompt → call LLaMA

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from app.vector.chroma_store import fetch_parent_texts, vectorstore
from langchain_ollama import OllamaLLM as LangChainOllama
from app.tools.file_reader_tool import file_reader_tool, store_file, clear_file

llm = LangChainOllama(model="llama3.2:3b")

def format_docs(docs)->str:

    # Bridge between retriever output and prompt input.
    # Retriever returns child docs with parent_id in metadata.
    # We fetch full parent text from ChromaDB using those parent_ids.
    # Returns combined context string for the prompt.    

    parents_id=list({
        doc.metadata["parent_id"]
        for doc in docs
        if doc.metadata.get("parent_id")
    })

    if not parents_id:
        return "No context found in the document."
    
    parent_texts = fetch_parent_texts(parents_id)
    return "\n\n---\n\n".join(parent_texts)   

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

#Prompt for direct file reading 
file_prompt = ChatPromptTemplate.from_template("""
You are a file assistant. The user has uploaded a file.
answer the questions from file choosed.
Quote directly from the file content where possible.
If the answer is not in the file, say "This information is not in the file."   
                                               
File Content:
{file_content}
                                               
Question: {question}
                                               
Answer:
""")

def build_rag_chain(pdf_id: str):
    # Build a RAG chain for a specific PDF.
    # Each PDF gets its own retriever filtered by pdf_id.

    # Step 1 — create retriever filtered to this PDF's child chunks only
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": {
                "$and": [
                    {"pdf_id": {"$eq": pdf_id}},
                    {"chunk_type": {"$eq": "child"}}
                ]
            }
        }
    )

    # Step 2 — build the LCEL chain using | operator
    chain = (
        {
            "context": retriever | format_docs,  # question → retriever → format_docs → context string
            "question": RunnablePassthrough()     # question passes through unchanged
        }
        | rag_prompt        # fills {context} and {question} into prompt
        | llm               # sends filled prompt to LLaMA
        | StrOutputParser() # converts LLM output to clean string
    )

    return chain

def build_file_chain():
    #Simple chain for direct file reading.
    # File content already extracted before chain runs.
    # Just fills prompt and calls LLM.

    chain = (
        {
            "file_content": RunnablePassthrough() | (lambda x:x["file_content"]), # file content passed in directly
            "question": RunnablePassthrough() | (lambda x: x["question"] )# question passes through unchanged
        }
        | file_prompt
        | llm 
        | StrOutputParser()
    )
    return chain

def answer_with_file(
    question: str,
    filename: str,
    file_bytes: bytes
) -> str:
    store_file(filename, file_bytes)

    try:
        # Extract full text using tool
        file_content = file_reader_tool.invoke(filename)

        if file_content.startswith("File too large") or file_content.startswith("Unsupported"):
            return file_content

        # Return content directly without sending to LLaMA
        return file_content

    finally:
        clear_file(filename)


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
    # Build chain for this specific PDF and invoke it with the question.
    # Chain handles everything: search → fetch context → prompt → LLaMA → answer

    chain = build_rag_chain(pdf_id)

    # Single invoke call replaces all our manual steps
    answer = chain.invoke(question)

    return answer