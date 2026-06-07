# ollama_llm.py
# Implements BaseLLM using Ollama running locally.
# Ollama must be running and the model must be pulled before using this.

import ollama
from app.llm.base import BaseLLM
from typing import List, Dict

class OllamaLLM(BaseLLM):

    def __init__(self, model_name: str = "llama3.2:3b"):
        # Store which model to use — easy to swap later
        self.model_name = model_name

    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Send full conversation history to Ollama and get a reply
        response = ollama.chat(
            model=self.model_name,
            messages=messages
        )
        # Extract just the text content from the response
        return response["message"]["content"]