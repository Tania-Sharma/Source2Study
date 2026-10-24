
from backend.ai.models import ResourceContext, RetrievedChunk


def build_resource_context(
    query: str,
    retrieved_chunks: list[dict],
) -> ResourceContext:
    """Convert RAG dictionaries into the standard ResourceContext."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    if not isinstance(retrieved_chunks, list):
        raise ValueError("retrieved_chunks must be a list.")

    chunks = []

    for index, chunk in enumerate(retrieved_chunks):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"Retrieved chunk at index {index} must be a dictionary."
            )

        text = chunk.get("text")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"Retrieved chunk at index {index} must contain non-empty text."
            )

        metadata = chunk.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        score = chunk.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            score = None

        chunks.append(
            RetrievedChunk(
                text=text.strip(),
                metadata=metadata,
                score=score,
            )
        )

    return ResourceContext(
        query=query.strip(),
        retrieved_chunks=chunks,
    )
