from typing import Protocol

from langchain_ollama import OllamaEmbeddings

from app.core.config import get_settings


class EmbeddingProvider(Protocol):
    def embed_product(self, text: str) -> list[float]: ...


class OllamaProductEmbeddingProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.expected_dimension = settings.embedding_dimension
        self.embeddings = OllamaEmbeddings(
            base_url=settings.ollama_embedding_base_url,
            model=settings.ollama_embedding_model,
        )

    def embed_product(self, text: str) -> list[float]:
        vector = self.embeddings.embed_query(text)
        if len(vector) != self.expected_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.expected_dimension}, got {len(vector)}"
            )
        return vector

