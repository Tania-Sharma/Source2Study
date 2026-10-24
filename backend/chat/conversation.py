from datetime import datetime


class Conversation:
    """
    Represents one conversation between a student and Source2Study.

    A conversation can contain multiple user and assistant messages.
    """

    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        resource_id: str | None = None,
        title: str = "New Conversation",
    ):
        if not conversation_id:
            raise ValueError(
                "conversation_id must be provided."
            )

        if not user_id:
            raise ValueError(
                "user_id must be provided."
            )

        self.conversation_id = conversation_id
        self.user_id = user_id
        self.resource_id = resource_id
        self.title = title

        self.messages = []

        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def add_message(
        self,
        role: str,
        content: str,
    ) -> dict:
        """
        Add a message to the conversation.

        role can be:
        - user
        - assistant
        """

        if role not in {"user", "assistant"}:
            raise ValueError(
                "role must be user or assistant."
            )

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "content must be a non-empty string."
            )

        message = {
            "role": role,
            "content": content.strip(),
            "created_at": datetime.now(),
        }

        self.messages.append(message)
        self.updated_at = message["created_at"]

        return message

    def get_messages(self) -> list[dict]:
        """Return all messages in this conversation."""

        return self.messages.copy()

    def get_message_count(self) -> int:
        """Return the total number of messages."""

        return len(self.messages)

    def get_last_message(self) -> dict | None:
        """Return the latest message, if available."""

        if not self.messages:
            return None

        return self.messages[-1]