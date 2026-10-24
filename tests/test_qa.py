from backend.ai.qa import answer_question


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return "Normalization reduces redundancy."


def test_answer_question():

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

    result = answer_question(
        question="What is normalization?",
        retrieved_chunks=rag_output,
        llm_client=FakeLLM(),
    )

    assert result["answer"] == "Normalization reduces redundancy."
    assert result["sources"] == ["DBMS.pdf"]