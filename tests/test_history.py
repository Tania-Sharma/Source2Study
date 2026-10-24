from backend.chat.conversation import Conversation
from backend.chat.history import ConversationHistory


def test_conversation_history():

    conversation = Conversation(
        conversation_id="conv_001",
        user_id="user_001",
        title="DBMS Discussion",
    )

    conversation.add_message(
        "user",
        "What is normalization?",
    )

    conversation.add_message(
        "assistant",
        "Normalization reduces data redundancy.",
    )

    conversation.add_message(
        "user",
        "What is 1NF?",
    )

    conversation.add_message(
        "assistant",
        "1NF requires atomic values.",
    )

    history = ConversationHistory(
        conversation
    )

    all_messages = history.get_history()

    assert len(all_messages) == 4

    recent_messages = history.get_recent_history(
        limit=2
    )

    assert len(recent_messages) == 2

    assert recent_messages[0]["role"] == "user"
    assert recent_messages[1]["role"] == "assistant"

    llm_history = history.build_llm_history()

    assert "User: What is normalization?" in llm_history
    assert (
        "Assistant: Normalization reduces data redundancy."
        in llm_history
    )
    assert "User: What is 1NF?" in llm_history
    assert (
        "Assistant: 1NF requires atomic values."
        in llm_history
    )


def test_recent_history_limit():

    conversation = Conversation(
        conversation_id="conv_002",
        user_id="user_001",
    )

    for number in range(5):
        conversation.add_message(
            "user",
            f"Message {number}",
        )

    history = ConversationHistory(
        conversation
    )

    recent_messages = history.get_recent_history(
        limit=2
    )

    assert len(recent_messages) == 2
    assert recent_messages[0]["content"] == "Message 3"
    assert recent_messages[1]["content"] == "Message 4"