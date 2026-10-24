from backend.chat.chat_manager import ChatManager


def test_chat_manager():

    manager = ChatManager()

    conversation = manager.create_conversation(
        conversation_id="conv_001",
        user_id="user_001",
        resource_id="DBMS.pdf",
        title="DBMS Discussion",
    )

    assert conversation.conversation_id == "conv_001"
    assert conversation.user_id == "user_001"
    assert conversation.resource_id == "DBMS.pdf"

    manager.add_message(
        "conv_001",
        "user",
        "What is normalization?",
    )

    manager.add_message(
        "conv_001",
        "assistant",
        "Normalization reduces data redundancy.",
    )

    conversation = manager.get_conversation(
        "conv_001"
    )

    assert conversation.get_message_count() == 2

    messages = conversation.get_messages()

    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    conversations = manager.list_conversations(
        user_id="user_001"
    )

    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == "conv_001"
    assert conversations[0]["message_count"] == 2


def test_delete_conversation():

    manager = ChatManager()

    manager.create_conversation(
        conversation_id="conv_002",
        user_id="user_001",
    )

    manager.delete_conversation("conv_002")

    assert len(manager.conversations) == 0