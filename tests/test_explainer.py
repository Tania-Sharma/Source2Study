from backend.ai.explainer import explain_topic


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return (
            "Normalization is a database design technique "
            "used to reduce data redundancy."
        )


def test_explain_topic():

    rag_output = [
        {
            "text": "Normalization reduces redundancy in databases.",
            "metadata": {
                "source": "DBMS.pdf",
                "page": 10,
            },
            "score": 0.92,
        },
        {
            "text": "Normalization organizes data into related tables.",
            "metadata": {
                "source": "DBMS.pdf",
                "page": 11,
            },
            "score": 0.87,
        },
    ]

    result = explain_topic(
        topic="Normalization",
        retrieved_chunks=rag_output,
        llm_client=FakeLLM(),
    )

    assert "Normalization" in result["explanation"]
    assert result["sources"] == ["DBMS.pdf"]