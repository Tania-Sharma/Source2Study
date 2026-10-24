import json

from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient
from backend.ai.prompts import build_quiz_prompt


def generate_quiz(
    retrieved_chunks: list[dict],
    number_of_questions: int = 5,
    difficulty: str = "medium",
    topic: str | None = None,
    llm_client: LLMClient | None = None,
) -> dict:
    """
    Generate a resource-grounded quiz.

    Args:
        retrieved_chunks: Chunks retrieved from the RAG layer.
        number_of_questions: Number of questions to generate.
        difficulty: Quiz difficulty: easy, medium, or hard.
        topic: Optional topic to focus on.
        llm_client: Optional LLM client, useful for testing.

    Returns:
        Dictionary containing quiz information and sources.
    """

    if not isinstance(retrieved_chunks, list):
        raise ValueError("retrieved_chunks must be a list.")

    if number_of_questions < 1:
        raise ValueError(
            "number_of_questions must be at least 1."
        )

    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError(
            "difficulty must be easy, medium, or hard."
        )

    resource_context = build_resource_context(
        query=topic or "Generate a quiz from the resource.",
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "title": "Quiz",
            "difficulty": difficulty,
            "questions": [],
            "sources": [],
            "message": (
                "I could not find enough information in the "
                "provided resource to create a quiz."
            ),
        }

    prompt = build_quiz_prompt(
        context=context_text,
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        topic=topic,
    )

    client = llm_client or LLMClient()

    raw_response = client.generate(prompt)

    try:
        quiz = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON for the quiz."
        ) from exc

    if not isinstance(quiz, dict):
        raise ValueError("Quiz response must be a JSON object.")

    questions = quiz.get("questions")

    if not isinstance(questions, list):
        raise ValueError(
            "Quiz response must contain a questions list."
        )

    if len(questions) != number_of_questions:
        raise ValueError(
            "LLM returned an incorrect number of questions."
        )

    for question in questions:
        required_fields = {
            "question",
            "answer",
            "explanation",
            "source_reference",
        }

        if not isinstance(question, dict):
            raise ValueError("Each quiz question must be an object.")

        if not required_fields.issubset(question):
            raise ValueError(
                "A quiz question is missing required fields."
            )

    quiz["difficulty"] = difficulty
    quiz["sources"] = resource_context.get_sources()

    return quiz