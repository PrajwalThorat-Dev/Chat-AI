# LangChain Integration — Chat-AI

## Overview
This document summarizes the LangChain components integrated into the Chat-AI RAG pipeline, replacing manual implementations with standardized LangChain abstractions.

---

## Phases Implemented

### Phase A — OllamaEmbeddings (Batch Embedding)
**File:** `app/vector/chroma_store.py`

**Before:** Single embedding call per chunk using raw `ollama.embeddings()` in a loop.

**After:** Replaced with `LangChain OllamaEmbeddings` supporting batch embedding — all child chunks embedded in a single call.

**Impact:** Significant upload speed improvement for large documents. A 350-page book with ~2000 child chunks goes from 2000 individual Ollama calls to a single batched call.

```python
from langchain_ollama.embeddings import OllamaEmbeddings
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
embeddings = embedding_model.embed_documents(texts)  # batch
```

---

### Phase B — PyMuPDFLoader (Document Loading)
**File:** `app/services/pdf_service.py`

**Before:** Manual PDF extraction using `fitz.open()` with page-by-page text loop. No metadata available.

**After:** Replaced with `LangChain PyMuPDFLoader` which returns structured `Document` objects with automatic metadata.

**Impact:** Each extracted page now carries metadata (`page_number`, `source`, `author`, `total_pages`) enabling future page-level attribution in answers.

```python
from langchain_community.document_loaders import PyMuPDFLoader
loader = PyMuPDFLoader(file_path)
documents = loader.load()  # returns Document objects with metadata
```

---

### Phase C — LangChain Chroma Wrapper
**File:** `app/vector/chroma_store.py`

**Before:** Raw ChromaDB `collection.query()` calls with manual embedding injection.

**After:** Integrated `LangChain Chroma` vectorstore wrapper alongside raw collection for parent/child operations requiring fine-grained control.

**Impact:** Cleaner similarity search API with built-in embedding handling. Maintains raw collection access for parent entry storage with dummy vectors.

```python
from langchain_chroma import Chroma
vectorstore = Chroma(client=chroma_client, collection_name="document_chunks",
                     embedding_function=embedding_model)
results = vectorstore.similarity_search(query, k=3, filter={...})
```

---

### Phase D — ChatPromptTemplate (Prompt Management)
**File:** `app/services/rag_service.py`

**Before:** Plain Python f-string prompt built manually inside a function.

**After:** Replaced with `LangChain ChatPromptTemplate` — a reusable, testable prompt template with named variables.

**Impact:** Prompt logic is cleanly separated from pipeline logic. Easy to modify, version, or swap prompts without touching RAG flow.

```python
from langchain_core.prompts import ChatPromptTemplate
rag_prompt = ChatPromptTemplate.from_template("""
You are a document assistant...
Context: {context}
Question: {question}
""")
```

---

### Phase E — ChatMessageHistory (Conversation Memory)
**File:** `app/services/chat_service.py`

**Before:** Manual history list built from PostgreSQL query on every request.

**After:** Replaced with `LangChain ChatMessageHistory` — in-memory session store that loads from PostgreSQL on first use and maintains history for subsequent messages.

**Impact:** Reduced PostgreSQL reads for active sessions. History management standardized using LangChain message types (`HumanMessage`, `AIMessage`).

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
history_obj = ChatMessageHistory()
history_obj.add_message(HumanMessage(content=user_message))
```

---

## Architecture After Integration

```
PDF Upload:
PyMuPDFLoader → RecursiveCharacterTextSplitter → parent/child chunks
→ OllamaEmbeddings (batch) → ChromaDB (Chroma wrapper + raw collection)

RAG Query:
OllamaEmbeddings (query) → Chroma similarity_search
→ fetch parent text → ChatPromptTemplate → LLaMA → answer

Normal Chat:
ChatMessageHistory (load from PG once) → LLaMA → save to PG + memory
```

---

## Packages Added

```
langchain-ollama       — OllamaEmbeddings
langchain-community    — PyMuPDFLoader, ChatMessageHistory
langchain-chroma       — Chroma vectorstore wrapper
langchain-core         — ChatPromptTemplate, HumanMessage, AIMessage
langchain              — Core framework
```

---

## What Was Not Changed
- FastAPI routes and models
- PostgreSQL chat history storage
- ChromaDB parent-child architecture
- Ollama LLaMA model integration
- Frontend (React + TypeScript)
