from app.llm.base import BaseLLM
from typing import List, Dict

class MockLLM(BaseLLM):
    def generate(self, messages: List[Dict[str, str]]) -> str:
        last = messages[-1]["content"] if messages else ""
        return f"You said: '{last}'"