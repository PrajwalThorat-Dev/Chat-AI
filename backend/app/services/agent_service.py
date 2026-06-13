# agent_service.py
# ReAct agent using LangGraph and ChatOllama.
# ChatOllama supports tool binding required by LangGraph agent.

from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from app.tools.file_reader_tool import file_reader_tool

# ChatOllama supports bind_tools — required for LangGraph agent
llm = ChatOllama(model="llama3.2:3b")

tools = [file_reader_tool]

def build_agent():
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a helpful assistant. Give only the final answer. Never mention tool names, internal steps, or reasoning in your response."
    )
    return agent

def clean_response(text: str) -> str:
    # Remove common internal phrases LLaMA adds
    phrases_to_remove = [
        r"I've uploaded the file\.\s*",
        r"Reading [A-Za-z]:\\[\w\\.\- ]+:\s*",
        r"Reading \/[\w\/.\-]+:\s*",
    ]
    import re
    for pattern in phrases_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()

def answer_with_agent(question: str) -> str:
    agent = build_agent()

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    messages = result["messages"]

    # walk messages in reverse, find last clean AI response
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "ai":
            if not getattr(msg, "tool_calls", None):
                content = msg.content
                # if content is a list extract text
                if isinstance(content, list):
                    content = " ".join(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict)
                    )
                if content.strip():
                    return content.strip()

    return clean_response(content.strip())
