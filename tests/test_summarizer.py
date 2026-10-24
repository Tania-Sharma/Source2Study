from backend.ai.summarizer import summarize_resource


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return (
            "Normalization organizes data to reduce redundancy. "
            "1NF requires atomic values."
        )


def test_summarize_resource():

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

    result = summarize_resource(
        retrieved_chunks=rag_output,
        llm_client=FakeLLM(),
    )

    assert "Normalization" in result["summary"]
    assert result["sources"] == ["DBMS.pdf"]