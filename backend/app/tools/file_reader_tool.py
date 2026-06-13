# file_reader_tool.py
# Handles text extraction from multiple file types.
# Exposes a LangChain tool that chains can call automatically.

import json
import tempfile
import os
import pandas as pd
from docx import Document as DocxDocument
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.tools import tool

# Max characters for direct context
MAX_CHARS = 50000

def read_pdf(file_bytes: bytes) -> str:
    # Extract text from PDF using PyMuPDFLoader
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        loader = PyMuPDFLoader(tmp_path)
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])
    finally:
        os.unlink(tmp_path)

def read_txt(file_bytes: bytes) -> str:
    # Decode plain text file
    return file_bytes.decode("utf-8", errors="ignore")

def read_csv(file_bytes: bytes) -> str:
    # Read CSV and convert to readable string
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        df = pd.read_csv(tmp_path)
        return df.to_string(index=False)
    finally:
        os.unlink(tmp_path)

def read_docx(file_bytes: bytes) -> str:
    # Extract text from Word document
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        doc = DocxDocument(tmp_path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    finally:
        os.unlink(tmp_path)

def read_json(file_bytes: bytes) -> str:
    # Parse and pretty print JSON
    data = json.loads(file_bytes.decode("utf-8"))
    return json.dumps(data, indent=2)

def read_code(file_bytes: bytes) -> str:
    # Read code or markdown as plain text
    return file_bytes.decode("utf-8", errors="ignore")

# Extension to handler mapping
EXTENSION_HANDLERS = {
    ".pdf":  read_pdf,
    ".txt":  read_txt,
    ".csv":  read_csv,
    ".docx": read_docx,
    ".json": read_json,
    ".py":   read_code,
    ".js":   read_code,
    ".ts":   read_code,
    ".md":   read_code,
}

def extract_text(filename: str, file_bytes: bytes) -> str:
    # Route to correct handler based on file extension
    ext = os.path.splitext(filename)[1].lower()

    if ext not in EXTENSION_HANDLERS:
        return f"Unsupported file type: {ext}. Supported: {list(EXTENSION_HANDLERS.keys())}"

    text = EXTENSION_HANDLERS[ext](file_bytes)

    if len(text) > MAX_CHARS:
        return f"File too large ({len(text)} chars). Limit is {MAX_CHARS}. Use PDF upload for RAG mode."

    return text

def read_from_path(file_path: str) -> str:
    # Read file directly from disk using absolute path.
    # Detects file type from extension and uses correct handler.

    if not os.path.exists(file_path):
        return f"File not found at path: {file_path}"

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in EXTENSION_HANDLERS:
        return f"Unsupported file type: {ext}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return extract_text(filename, file_bytes)

# Temporary file store — bytes stored here, tool reads by filename
_file_store: dict[str, bytes] = {}

def store_file(filename: str, file_bytes: bytes):
    # Store file bytes temporarily before tool runs
    _file_store[filename] = file_bytes

def clear_file(filename: str):
    # Clean up after tool finishes
    _file_store.pop(filename, None)

@tool
def file_reader_tool(input: str) -> str:
    """
    Reads a file and returns its full text content.
    Use this tool when the user provides a file path in their message.
    Input should be the complete file path string exactly as provided by the user.
    Returns the full text content of the file.
    """
    # if input looks like a Windows or Unix path, read from disk
    if os.path.sep in input or (len(input) > 3 and input[1] == ":"):
        return read_from_path(input)

    # otherwise read from temporary store (UI upload)
    file_bytes = _file_store.get(input)
    if not file_bytes:
        return f"File '{input}' not found."

    return extract_text(input, file_bytes)