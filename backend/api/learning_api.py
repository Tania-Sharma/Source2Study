from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.rag.retriever import retrieve
from backend.ai.summarizer import summarize_resource
from backend.ai.explainer import explain_topic
from backend.quiz.quiz_generator import generate_quiz
from backend.quiz.mcq_generator import generate_mcqs
from backend.quiz.quiz_evaluator import evaluate_quiz

router = APIRouter(
    tags=["Learning Assistant"],
)


class SummarizeRequest(BaseModel):
    query: str = Field(default="Summarize the core concepts.", min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ExplainRequest(BaseModel):
    topic: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class QuizGenerateRequest(BaseModel):
    topic: str | None = None
    number_of_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium")
    top_k: int = Field(default=5, ge=1, le=20)


class EvaluateRequest(BaseModel):
    questions: list[dict[str, Any]]
    user_answers: list[str | None]


@router.post("/ai/summarize")
def api_summarize(request: SummarizeRequest):
    try:
        chunks = retrieve(request.query, top_k=request.top_k)
        result = summarize_resource(retrieved_chunks=chunks, query=request.query)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ai/explain")
def api_explain(request: ExplainRequest):
    try:
        chunks = retrieve(request.topic, top_k=request.top_k)
        result = explain_topic(topic=request.topic, retrieved_chunks=chunks)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/quiz/generate")
def api_generate_quiz(request: QuizGenerateRequest):
    try:
        query = request.topic or "Generate a quiz from the study materials."
        chunks = retrieve(query, top_k=request.top_k)
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
        chunks = retrieve(query, top_k=request.top_k)
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
