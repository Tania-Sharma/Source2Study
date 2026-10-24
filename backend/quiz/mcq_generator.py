import json

from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient
from backend.ai.prompts import build_mcq_prompt


def generate_mcqs(
    retrieved_chunks: list[dict],
    number_of_questions: int = 5,
    difficulty: str = "medium",
    topic: str | None = None,
    llm_client: LLMClient | None = None,
) -> dict:
    """
    Generate resource-grounded multiple-choice questions.
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
        query=topic or "Generate MCQs from the resource.",
        retrieved_chunks=retrieved_chunks,
    )

    context_text = resource_context.get_context_text()

    if not context_text:
        return {
            "title": "MCQ Quiz",
            "difficulty": difficulty,
            "questions": [],
            "sources": [],
            "message": (
                "I could not find enough information in the "
                "provided resource to create MCQs."
            ),
        }

    prompt = build_mcq_prompt(
        context=context_text,
        number_of_questions=number_of_questions,
        difficulty=difficulty,
        topic=topic,
    )

    client = llm_client or LLMClient()

    raw_response = client.generate(prompt)

    try:
        mcq_quiz = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON for MCQs."
        ) from exc

    if not isinstance(mcq_quiz, dict):
        raise ValueError(
            "MCQ response must be a JSON object."
        )

    questions = mcq_quiz.get("questions")

    if not isinstance(questions, list):
        raise ValueError(
            "MCQ response must contain a questions list."
        )

    if len(questions) != number_of_questions:
        raise ValueError(
            "LLM returned an incorrect number of MCQs."
        )

    for question in questions:

        required_fields = {
            "question",
            "options",
            "correct_answer",
            "explanation",
            "source_reference",
        }

        if not isinstance(question, dict):
            raise ValueError(
                "Each MCQ must be an object."
            )

        if not required_fields.issubset(question):
            raise ValueError(
                "An MCQ is missing required fields."
            )

        options = question["options"]

        if not isinstance(options, list):
            raise ValueError(
                "MCQ options must be a list."
            )

        if len(options) != 4:
            raise ValueError(
                "Each MCQ must contain exactly 4 options."
            )

        if len(set(options)) != 4:
            raise ValueError(
                "MCQ options must be unique."
            )

        if question["correct_answer"] not in options:
            raise ValueError(
                "Correct answer must be one of the options."
            )

    mcq_quiz["difficulty"] = difficulty
    mcq_quiz["sources"] = resource_context.get_sources()

    return mcq_quiz