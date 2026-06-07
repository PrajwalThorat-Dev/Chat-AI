# base.py
# Abstract base class for all LLM integrations.
# Any new LLM (Ollama, OpenAI, etc.) must implement this interface.
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Takes a list of {"role": "user"/"assistant", "content": "..."}
        # Returns the assistant reply as a plain string
        pass