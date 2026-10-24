
from backend.chat.conversation import Conversation
from backend.chat.history import ConversationHistory
from backend.ai.qa import answer_conversational_question


class ChatManager:
    """Manage conversations and process questions using RAG and an LLM."""

    def __init__(self):
        # Temporary in-memory storage; database integration comes later.
        self.conversations = {}

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        resource_id: str | None = None,
        title: str = "New Conversation",
    ) -> Conversation:
        """Create and store a new conversation."""

        if not isinstance(conversation_id, str) or not conversation_id.strip():
            raise ValueError("conversation_id must be a non-empty string.")

        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string.")

        if conversation_id in self.conversations:
            raise ValueError("A conversation with this ID already exists.")

        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            resource_id=resource_id,
            title=title,
        )

        self.conversations[conversation_id] = conversation
        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        """Retrieve a conversation using its ID."""

        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found.")

        return self.conversations[conversation_id]

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> dict:
        """Add a message to an existing conversation."""

        conversation = self.get_conversation(conversation_id)

        return conversation.add_message(
            role=role,
            content=content,
        )

    def list_conversations(
        self,
        user_id: str | None = None,
    ) -> list[dict]:
        """Return conversation details, optionally filtered by user."""

        conversations = self.conversations.values()

        if user_id is not None:
            conversations = [
                conversation
                for conversation in conversations
                if conversation.user_id == user_id
            ]

        return [
            {
                "conversation_id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "resource_id": conversation.resource_id,
                "title": conversation.title,
                "message_count": conversation.get_message_count(),
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
            for conversation in conversations
        ]

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation from in-memory storage."""

        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found.")

        del self.conversations[conversation_id]

    def chat(
        self,
        conversation_id: str,
        question: str,
        retriever,
        llm_client=None,
        top_k: int = 5,
    ) -> dict:
        """
        Process a question using retrieval-augmented generation.

        Flow:
            Validate → Retrieve context → Generate answer
            → Save user and assistant messages → Return result
        """

        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string.")

        question = question.strip()

        if not callable(retriever):
            raise ValueError("retriever must be a callable function.")

        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise ValueError("top_k must be an integer.")

        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")

        conversation = self.get_conversation(conversation_id)

        # Build history before adding the current question.
        history = ConversationHistory(
            conversation
        ).build_llm_history(limit=10)

        # Retrieve relevant resource chunks.
        retrieved_chunks = retriever(question, top_k=top_k)

        if not isinstance(retrieved_chunks, list):
            raise ValueError("retriever must return a list.")

        # Generate the answer before saving messages.
        # If retrieval or generation fails, no incomplete turn is saved.
        result = answer_conversational_question(
            question=question,
            retrieved_chunks=retrieved_chunks,
            conversation_history=history,
            llm_client=llm_client,
        )

        if not isinstance(result, dict):
            raise RuntimeError("The QA module returned an invalid result.")

        answer = result.get("answer")
        sources = result.get("sources", [])

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The QA module returned an empty answer.")

        if not isinstance(sources, list):
            sources = []

        # Save the completed conversation turn.
        conversation.add_message(
            role="user",
            content=question,
        )

        conversation.add_message(
            role="assistant",
            content=answer.strip(),
        )

        return {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer.strip(),
            "sources": sources,
            "history": ConversationHistory(
                conversation
            ).get_history(),
        }
