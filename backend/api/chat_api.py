from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.chat.chat_manager import ChatManager
from backend.rag.retriever import retrieve


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


chat_manager = ChatManager()


class ChatRequest(BaseModel):
    """
    Data received from the frontend when a student
    sends a chat message.
    """

    conversation_id: str = Field(
        min_length=1
    )

    question: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class ChatResponse(BaseModel):
    """
    Response returned to the frontend.
    """

    conversation_id: str
    question: str
    answer: str
    sources: list[str]
    history: list[dict[str, Any]]

class CreateConversationRequest(BaseModel):
    user_id: str = Field(
        min_length=1
    )

    resource_id: str | None = None

    title: str = Field(
        default="New Conversation",
        min_length=1,
    )


@router.post("/conversation")
def create_conversation(
    request: CreateConversationRequest,
):
    """
    Create a new conversation.
    """

    import uuid

    conversation_id = str(
        uuid.uuid4()
    )

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
            detail="Failed to process chat request.",
        ) from exc