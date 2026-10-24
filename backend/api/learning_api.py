import json
import re
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.rag.retriever import retrieve
from backend.ai.summarizer import summarize_resource
from backend.ai.explainer import explain_topic
from backend.quiz.quiz_generator import generate_quiz
from backend.quiz.mcq_generator import generate_mcqs
from backend.quiz.quiz_evaluator import evaluate_quiz
from backend.ai.context_adapter import build_resource_context
from backend.ai.llm import LLMClient

router = APIRouter(
    tags=["Learning Assistant"],
)


class SummarizeRequest(BaseModel):
    query: str = Field(default="Summarize the core concepts.", min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    resource_id: str | None = None


class ExplainRequest(BaseModel):
    topic: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    resource_id: str | None = None
    style: str | None = "standard"  # standard, beginner, steps, analogy, exam


class QuizGenerateRequest(BaseModel):
    topic: str | None = None
    number_of_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium")
    top_k: int = Field(default=5, ge=1, le=20)
    resource_id: str | None = None


class EvaluateRequest(BaseModel):
    questions: list[dict[str, Any]]
    user_answers: list[str | None]


class AnswerEvaluateRequest(BaseModel):
    question: str = Field(min_length=1)
    student_answer: str = Field(min_length=1)
    resource_id: str | None = None
    reference_answer: str | None = None


@router.post("/ai/summarize")
def api_summarize(request: SummarizeRequest):
    try:
        chunks = retrieve(request.query, top_k=request.top_k, resource_id=request.resource_id)
        result = summarize_resource(retrieved_chunks=chunks, query=request.query)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ai/explain")
def api_explain(request: ExplainRequest):
    try:
        topic_query = request.topic
        if request.style == "beginner":
            topic_query = f"{request.topic} (explain for complete beginner without jargon)"
        elif request.style == "steps":
            topic_query = f"{request.topic} (step-by-step breakdown)"
        elif request.style == "analogy":
            topic_query = f"{request.topic} (real-world analogy and practical example)"
        elif request.style == "exam":
            topic_query = f"{request.topic} (high-yield exam revision and definitions)"

        chunks = retrieve(request.topic, top_k=request.top_k, resource_id=request.resource_id)
        result = explain_topic(topic=topic_query, retrieved_chunks=chunks)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/quiz/generate")
def api_generate_quiz(request: QuizGenerateRequest):
    try:
        query = request.topic or "Generate a quiz from the study materials."
        chunks = retrieve(query, top_k=request.top_k, resource_id=request.resource_id)
        result = generate_quiz(
            retrieved_chunks=chunks,
            number_of_questions=request.number_of_questions,
            difficulty=request.difficulty,
            topic=request.topic,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/quiz/mcq")
def api_generate_mcq(request: QuizGenerateRequest):
    try:
        query = request.topic or "Generate multiple choice questions."
        chunks = retrieve(query, top_k=request.top_k, resource_id=request.resource_id)
        result = generate_mcqs(
            retrieved_chunks=chunks,
            number_of_questions=request.number_of_questions,
            difficulty=request.difficulty,
            topic=request.topic,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/quiz/evaluate")
def api_evaluate_quiz(request: EvaluateRequest):
    try:
        result = evaluate_quiz(
            questions=request.questions,
            user_answers=request.user_answers,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ai/evaluate-answer")
@router.post("/quiz/evaluate-answer")
def api_evaluate_answer(request: AnswerEvaluateRequest):
    """Evaluate a student's answer using resource context and an LLM."""

    if not request.student_answer.strip():
        raise HTTPException(
            status_code=400,
            detail="Student answer cannot be empty.",
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Always initialize these so retrieval failures do not cause
    # uninitialized-variable errors in the fallback logic.
    chunks = []
    context_text = ""
    sources = []

    try:
        # Retrieve relevant learning material.
        try:
            chunks = retrieve(
                request.question,
                top_k=5,
                resource_id=request.resource_id,
            )
            chunks = chunks or []
        except Exception:
            chunks = []

        # Build context safely, even if retrieval returned nothing.
        try:
            resource_ctx = build_resource_context(
                query=request.question,
                retrieved_chunks=chunks,
            )
            context_text = str(
                resource_ctx.get_context_text() or ""
            )
            sources = resource_ctx.get_sources() or []
        except Exception:
            context_text = ""
            sources = []

        # First attempt: evaluate using the configured LLM.
        try:
            llm = LLMClient()

            reference_text = (
                f"Reference/Expected Answer: {request.reference_answer}"
                if request.reference_answer
                else "No reference answer was supplied."
            )

            prompt = f"""
You are Source2Study, an expert academic tutor.

Evaluate the student's answer fairly and constructively.
Use the reference context when available. If no context is available,
evaluate using general academic accuracy. Do not invent citations.

Question:
{request.question}

Reference Context:
{context_text if context_text else "No specific textbook context provided."}

{reference_text}

Student's Answer:
{request.student_answer}

Return ONLY a valid JSON object with this structure:
{{
    "score": 7,
    "max_score": 10,
    "percentage": 70,
    "verdict": "Proficient",
    "feedback": "Constructive feedback in 2-3 sentences.",
    "strengths": ["Strength one", "Strength two"],
    "improvements": ["Improvement one", "Improvement two"],
    "ideal_answer": "A comprehensive model answer."
}}

Rules:
- score must be an integer from 1 to 10.
- max_score must be 10.
- percentage must be an integer from 10 to 100.
- verdict must be one of Excellent, Proficient,
  Partially Correct, or Needs Improvement.
- strengths and improvements must be JSON arrays of strings.
- Do not include Markdown fences around the JSON.
"""

            raw = llm.generate(prompt)

            if not isinstance(raw, str):
                raw = str(raw)

            # Support responses containing plain JSON or a JSON code block.
            cleaned = raw.strip()
            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                cleaned,
                flags=re.IGNORECASE,
            ).strip()

            try:
                data = json.loads(cleaned)
            except json.JSONDecodeError:
                # Some models add explanatory text around the JSON.
                match = re.search(
                    r"\{.*\}",
                    cleaned,
                    re.DOTALL,
                )
                if not match:
                    raise ValueError(
                        "The AI did not return a valid JSON response."
                    )
                data = json.loads(match.group(0))

            if not isinstance(data, dict):
                raise ValueError(
                    "The AI response must be a JSON object."
                )

            score = max(1, min(10, int(data.get("score", 5))))

            verdict = str(
                data.get("verdict")
                or (
                    "Excellent" if score >= 9
                    else "Proficient" if score >= 7
                    else "Partially Correct" if score >= 5
                    else "Needs Improvement"
                )
            )

            valid_verdicts = {
                "Excellent",
                "Proficient",
                "Partially Correct",
                "Needs Improvement",
            }
            if verdict not in valid_verdicts:
                verdict = (
                    "Excellent" if score >= 9
                    else "Proficient" if score >= 7
                    else "Partially Correct" if score >= 5
                    else "Needs Improvement"
                )

            strengths = data.get("strengths", [])
            improvements = data.get("improvements", [])

            if not isinstance(strengths, list):
                strengths = []
            if not isinstance(improvements, list):
                improvements = []

            return {
                "question": request.question,
                "submitted_answer": request.student_answer,
                "score": score,
                "max_score": 10,
                "percentage": score * 10,
                "verdict": verdict,
                "feedback": str(
                    data.get("feedback")
                    or "Review the strengths and improvements below."
                ),
                "strengths": strengths,
                "improvements": improvements,
                "ideal_answer": str(
                    data.get("ideal_answer")
                    or "Review the relevant learning material for a complete answer."
                ),
                "sources": sources,
            }

        except Exception:
            # If the LLM fails, continue with a transparent,
            # simple heuristic fallback.
            pass

        # Fallback evaluation when the LLM is unavailable.
        answer = request.student_answer.strip()
        words = answer.split()
        word_count = len(words)

        question_terms = set(
            re.findall(r"\w{4,}", request.question.lower())
        )
        answer_terms = set(
            re.findall(r"\w{4,}", answer.lower())
        )
        context_terms = (
            set(re.findall(r"\w{4,}", context_text.lower()))
            if context_text
            else set()
        )

        comparison_terms = context_terms or question_terms
        overlap = len(answer_terms.intersection(comparison_terms))

        if word_count < 6:
            score = 3
            verdict = "Needs Improvement"
            feedback = (
                "Your answer is very brief. Include more explanation, "
                "relevant concepts, and key definitions."
            )
        elif word_count < 15:
            score = 5 + min(overlap, 2)
            verdict = "Partially Correct"
            feedback = (
                "You have the general idea, but need more technical "
                "detail and elaboration."
            )
        elif overlap >= 4:
            score = 9
            verdict = "Excellent"
            feedback = (
                "Your answer includes several relevant concepts. "
                "Verify details against the learning material."
            )
        else:
            score = 7 + min(overlap, 1)
            verdict = "Proficient"
            feedback = (
                "Your answer addresses the question. Adding relevant "
                "definitions, evidence, or examples could improve it."
            )

        if context_text:
            ideal_answer = context_text[:350]
            if len(context_text) > 350:
                ideal_answer += "..."
        else:
            ideal_answer = (
                f"A complete answer to '{request.question}' should "
                "define the main concept, explain its key points, "
                "and include a relevant example where appropriate."
            )

        return {
            "question": request.question,
            "submitted_answer": answer,
            "score": score,
            "max_score": 10,
            "percentage": score * 10,
            "verdict": verdict,
            "feedback": feedback,
            "strengths": [
                "Submitted an answer related to the question.",
                f"Answer contains {word_count} words.",
            ],
            "improvements": [
                "Include relevant technical definitions and details.",
                "Explain the concept with evidence or an example.",
            ],
            "ideal_answer": ideal_answer,
            "sources": sources,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Answer evaluation failed. Please try again.",
        ) from exc