
from typing import Any

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """A chunk returned by the RAG retrieval layer."""

    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class ResourceContext(BaseModel):
    """Standard interface between the RAG layer and AI layer."""

    query: str
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)

    def get_context_text(self) -> str:
        """Combine retrieved chunks into LLM-readable context."""

        return "\n\n".join(
            chunk.text.strip()
            for chunk in self.retrieved_chunks
            if chunk.text and chunk.text.strip()
        )

    def get_sources(self) -> list[str]:
        """Extract unique source names from retrieved chunk metadata."""

        sources = []

        for chunk in self.retrieved_chunks:
            metadata = chunk.metadata or {}

            source = (
                metadata.get("source_name")
                or metadata.get("source")
                or metadata.get("file_name")
                or metadata.get("filename")
                or metadata.get("url")
            )

            if source:
                source = str(source).strip()
                if source and source not in sources:
                    sources.append(source)

        return sources
