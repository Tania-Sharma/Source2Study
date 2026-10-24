from typing import Any
import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.chat.chat_manager import ChatManager
from backend.chat.history import ConversationHistory
from backend.rag.retriever import retrieve


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


chat_manager = ChatManager()


class ChatRequest(BaseModel):
    conversation_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    conversation_id: str
    question: str
    answer: str
    sources: list[str]
    history: list[dict[str, Any]]


class CreateConversationRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resource_id: str | None = None
    title: str = Field(default="New Conversation", min_length=1)


@router.post("/conversation")
def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation.
    """
    conversation_id = str(uuid.uuid4())

    conversation = chat_manager.create_conversation(
        conversation_id=conversation_id,
        user_id=request.user_id,
        resource_id=request.resource_id,
        title=request.title,
    )

    return {
        "conversation_id": conversation.conversation_id,
        "user_id": conversation.user_id,
        "resource_id": conversation.resource_id,
        "title": conversation.title,
    }


@router.get("/conversations")
def list_conversations(user_id: str | None = Query(None)):
    """
    List conversations, optionally filtered by user_id.
    """
    return chat_manager.list_conversations(user_id=user_id)


@router.get("/conversation/{conversation_id}")
def get_conversation(conversation_id: str):
    """
    Get a single conversation with its message history.
    """
    try:
        conv = chat_manager.get_conversation(conversation_id)
        history = ConversationHistory(conv).get_history()
        return {
            "conversation_id": conv.conversation_id,
            "user_id": conv.user_id,
            "resource_id": conv.resource_id,
            "title": conv.title,
            "history": history,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/conversation/{conversation_id}")
def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    """
    try:
        chat_manager.delete_conversation(conversation_id)
        return {"status": "success", "message": "Conversation deleted."}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):
    try:
        result = chat_manager.chat(
            conversation_id=request.conversation_id,
            question=request.question,
            retriever=retrieve,
            top_k=request.top_k,
        )
        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(exc)}",
        ) from exc
