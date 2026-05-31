from typing import Protocol
from langchain_ollama import OllamaLLM

from app.core.config import get_settings


class LlmClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class OllamaLlmClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.llm = OllamaLLM(
            base_url=settings.ollama_llm_base_url,
            model=settings.ollama_llm_model,
        )

    def generate(self, prompt: str) -> str:
        return str(self.llm.invoke(prompt) or "").strip()
