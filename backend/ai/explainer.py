from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient
from backend.ai.prompts import build_explanation_prompt


def explain_topic(
    topic: str,
    retrieved_chunks: list[dict],
    llm_client: LLMClient | None = None,
) -> dict:
    """
    Generate a simple, resource-grounded explanation of a topic.

    Args:
        topic: Topic the student wants to understand.
        retrieved_chunks: Chunks retrieved from the RAG layer.
        llm_client: Optional LLM client, useful for testing.

    Returns:
        Dictionary containing the explanation and source information.
    """

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("topic must be a non-empty string.")

    if not isinstance(retrieved_chunks, list):
        raise ValueError("retrieved_chunks must be a list.")

    resource_context = build_resource_context(
        query=topic,
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "explanation": (
                "I could not find enough information about this topic "
                "in the provided resource."
            ),
            "sources": resource_context.get_sources(),
        }

    prompt = build_explanation_prompt(
        topic=topic,
        context=context_text,
    )

    client = llm_client or LLMClient()

    explanation = client.generate(prompt)

    return {
        "explanation": explanation,
        "sources": resource_context.get_sources(),
    }