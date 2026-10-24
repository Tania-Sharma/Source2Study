from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient
from backend.ai.prompts import build_summary_prompt


def summarize_resource(
    retrieved_chunks: list[dict],
    llm_client: LLMClient | None = None,
    query: str = "Summarize the provided resource.",
) -> dict:
    """
    Generate a resource-grounded summary.

    Args:
        retrieved_chunks: Chunks retrieved from the RAG layer.
        llm_client: Optional LLM client, useful for testing.
        query: Query describing what should be summarized.

    Returns:
        Dictionary containing the summary and source information.
    """

    if not isinstance(retrieved_chunks, list):
        raise ValueError("retrieved_chunks must be a list.")

    resource_context = build_resource_context(
        query=query,
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "summary": (
                "I could not find enough information in the "
                "provided resource to create a summary."
            ),
            "sources": resource_context.get_sources(),
        }

    prompt = build_summary_prompt(context=context_text)

    client = llm_client or LLMClient()

    summary = client.generate(prompt)

    return {
        "summary": summary,
        "sources": resource_context.get_sources(),
    }