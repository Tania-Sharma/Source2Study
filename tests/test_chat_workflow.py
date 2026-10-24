from backend.chat.chat_manager import ChatManager


class FakeRetriever:
    def __call__(self, query, top_k=5):
        return [
            {
                "text": "Normalization reduces data redundancy.",
                "metadata": {
                    "source": "DBMS.pdf",
                    "page": 10,
                },
                "score": 0.92,
            },
            {
                "text": "1NF requires atomic values.",
                "metadata": {
                    "source": "DBMS.pdf",
                    "page": 11,
                },
                "score": 0.87,
            },
        ]


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return (
            "Normalization is a database design technique "
            "used to reduce data redundancy."
        )


def test_chat_workflow():

    manager = ChatManager()

    manager.create_conversation(
        conversation_id="conv_001",
        user_id="user_001",
        resource_id="DBMS.pdf",
        title="DBMS Discussion",
    )

    result = manager.chat(
        conversation_id="conv_001",
        question="What is normalization?",
        retriever=FakeRetriever(),
        llm_client=FakeLLM(),
    )

    assert result["conversation_id"] == "conv_001"

    assert result["question"] == (
        "What is normalization?"
    )

    assert "Normalization" in result["answer"]

    assert result["sources"] == ["DBMS.pdf"]

    assert len(result["history"]) == 2

    assert result["history"][0]["role"] == "user"

    assert result["history"][0]["content"] == (
        "What is normalization?"
    )

    assert result["history"][1]["role"] == "assistant"

    assert "Normalization" in (
        result["history"][1]["content"]
    )