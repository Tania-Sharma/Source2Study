from backend.chat.conversation import Conversation


class ConversationHistory:
    """
    Handle conversation history for Source2Study.

    This class prepares previous messages so that they can
    be used as context for the LLM.
    """

    def __init__(self, conversation: Conversation):
        if not isinstance(conversation, Conversation):
            raise ValueError(
                "conversation must be a Conversation object."
            )

        self.conversation = conversation

    def get_history(self) -> list[dict]:
        """
        Return all messages from the conversation.
        """

        return self.conversation.get_messages()

    def get_recent_history(
        self,
        limit: int = 10,
    ) -> list[dict]:
        """
        Return only the most recent messages.

        limit specifies the maximum number of messages to return.
        """

        if limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        messages = self.conversation.get_messages()

        return messages[-limit:]

    def build_llm_history(
        self,
        limit: int = 10,
    ) -> str:
        """
        Convert conversation history into a text format
        suitable for sending to the LLM.
        """

        recent_messages = self.get_recent_history(
            limit=limit
        )

        if not recent_messages:
            return ""

        history_parts = []

        for message in recent_messages:
            role = message["role"].capitalize()
            content = message["content"]

            history_parts.append(
                f"{role}: {content}"
            )

        return "\n\n".join(history_parts)