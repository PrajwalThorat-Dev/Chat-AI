# LangGraph ReAct Agent Integration — Chat-AI

## Overview
A LangGraph ReAct agent was integrated into the chat pipeline. When a user mentions a file path in their message, the agent automatically detects it, reads the file from disk using a LangChain tool, and answers the question based on the actual file content.

---

## How It Works

```
User message contains file path
        ↓
chat_service detects path using regex
        ↓
LangGraph ReAct agent triggered
        ↓
Agent thinks → decides to use file_reader_tool
        ↓
file_reader_tool reads file from disk
        ↓
Agent answers from actual file content
        ↓
Response cleaned → returned to user
```

---

## What is a ReAct Agent

ReAct = Reasoning + Acting. The agent thinks step by step before using a tool:

```
Thought:     "User gave a file path, I should read it"
Action:      file_reader_tool
Action Input: C:\Users\Admin\Documents\sample.csv
Observation: "Laptop, Phone, Desk, Chair..."
Thought:     "Now I can answer"
Final Answer: "The products listed are: Laptop, Phone..."
```

Unlike a chain (fixed steps), an agent decides on its own when and which tool to use.

---

## Files Created

### `backend/app/services/agent_service.py`
Core agent file. Contains:

**`build_agent()`** — Creates LangGraph ReAct agent with:
- `ChatOllama` model (llama3.2:3b) — chat model required for tool binding
- `file_reader_tool` in tools list
- System prompt telling agent to give only final answer, no internal reasoning

**`clean_response()`** — Post-processes agent response:
- Strips Windows and Unix file paths
- Removes leftover path references like "in [file] are:"

**`answer_with_agent()`** — Invokes agent and extracts clean final answer:
- Walks messages in reverse to find last clean AI response
- Skips tool call messages
- Applies `clean_response()` before returning

---

## Files Modified

### `backend/app/tools/file_reader_tool.py`
**Added `read_from_path()`** — reads file directly from absolute disk path:
- Checks if file exists at given path
- Detects file type from extension
- Opens file as bytes and passes to correct handler
- Returns extracted text content

**Updated `file_reader_tool` decorator** — now handles two modes:
```
Windows/Unix path detected → read_from_path()  (disk read)
Filename only              → _file_store lookup  (UI upload)
```

Path detection logic:
```python
if os.path.sep in input or (len(input) > 3 and input[1] == ":"):
    return read_from_path(input)
```

### `backend/app/services/chat_service.py`
**Added `has_file_path()`** — regex detects file path in message:
```python
windows_path = re.search(r'[A-Za-z]:\\[\w\\.\- ]+', message)
unix_path = re.search(r'\/[\w\/.\-]+\.\w+', message)
```

**Added agent mode to `handle_message()`** — new condition between RAG and normal chat:
```python
if pdf_id:          → RAG mode
elif has_file_path: → Agent mode  ← new
else:               → Normal chat
```

---

## Three Chat Modes After Integration

```
mode: "chat"   → normal LLaMA conversation (no pdf_id, no file path)
mode: "rag"    → PDF question answering (pdf_id provided)
mode: "rag"    → Agent file reading (file path detected in message)
```

Agent mode reuses "rag" display style on frontend — no frontend changes needed.

---

## Packages Added

```
langgraph   — LangGraph ReAct agent (create_react_agent)
```

---

## Supported File Types for Path-Based Reading

```
.pdf   .txt   .csv   .docx   .json   .py   .js   .ts   .md
```

---