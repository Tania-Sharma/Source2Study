from backend.ai.qa import answer_conversational_question


class FakeLLM:
    def generate(self, prompt: str) -> str:

        assert "What is normalization?" in prompt
        assert "Normalization reduces redundancy." in prompt

        return (
            "1NF is the first normal form of normalization "
            "and requires atomic values."
        )


def test_conversational_question():

    rag_output = [
        {
            "text": "Normalization reduces redundancy.",
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

    history = (
        "User: What is normalization?\n\n"
        "Assistant: Normalization reduces redundancy."
    )

    result = answer_conversational_question(
        question="Explain its first normal form.",
        retrieved_chunks=rag_output,
        conversation_history=history,
        llm_client=FakeLLM(),
    )

    assert "1NF" in result["answer"]
    assert result["sources"] == ["DBMS.pdf"]