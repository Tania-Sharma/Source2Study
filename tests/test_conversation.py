from backend.chat.conversation import Conversation


def test_conversation():

    conversation = Conversation(
        conversation_id="conv_001",
        user_id="user_001",
        resource_id="dbms_pdf",
        title="DBMS Discussion",
    )

    assert conversation.conversation_id == "conv_001"
    assert conversation.user_id == "user_001"
    assert conversation.resource_id == "dbms_pdf"
    assert conversation.title == "DBMS Discussion"

    assert conversation.get_message_count() == 0

    conversation.add_message(
        "user",
        "What is normalization?",
    )

    conversation.add_message(
        "assistant",
        "Normalization reduces data redundancy.",
    )

    assert conversation.get_message_count() == 2

    messages = conversation.get_messages()

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == (
        "What is normalization?"
    )

    assert messages[1]["role"] == "assistant"

    last_message = conversation.get_last_message()

    assert last_message["role"] == "assistant"