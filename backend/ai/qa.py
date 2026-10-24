from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient
from backend.ai.prompts import build_qa_prompt
from backend.ai.prompts import build_conversational_qa_prompt


def answer_question(
    question: str,
    retrieved_chunks: list[dict],
    llm_client: LLMClient | None = None,
) -> dict:
    """
    Generate a resource-grounded answer for a student's question.

    Args:
        question: Student's question.
        retrieved_chunks: Chunks returned by the RAG layer.
        llm_client: Optional LLM client, useful for testing.

    Returns:
        Dictionary containing the answer and source information.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string.")

    if not isinstance(retrieved_chunks, list):
        raise ValueError("retrieved_chunks must be a list.")

    resource_context = build_resource_context(
        query=question,
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "answer": (
                "I could not find relevant information in the "
                "provided resource."
            ),
            "sources": resource_context.get_sources(),
        }

    prompt = build_qa_prompt(
        question=question,
        context=context_text,
    )

    client = llm_client or LLMClient()

    answer = client.generate(prompt)

    return {
        "answer": answer,
        "sources": resource_context.get_sources(),

    }
def answer_conversational_question(
    question: str,
    retrieved_chunks: list[dict],
    conversation_history: str = "",
    llm_client: LLMClient | None = None,
) -> dict:
    """
    Generate a resource-grounded answer using previous
    conversation history as additional conversational context.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "question must be a non-empty string."
        )

    if not isinstance(retrieved_chunks, list):
        raise ValueError(
            "retrieved_chunks must be a list."
        )

    if not isinstance(conversation_history, str):
        raise ValueError(
            "conversation_history must be a string."
        )

    resource_context = build_resource_context(
        query=question,
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "answer": (
                "I could not find relevant information in the "
                "provided resource."
            ),
            "sources": resource_context.get_sources(),
        }

    prompt = build_conversational_qa_prompt(
        question=question,
        context=context_text,
        conversation_history=conversation_history,
    )

    client = llm_client or LLMClient()

    answer = client.generate(prompt)

    return {
        "answer": answer,
        "sources": resource_context.get_sources(),
    }