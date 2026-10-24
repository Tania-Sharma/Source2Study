from backend.quiz.quiz_generator import generate_quiz


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return """
        {
            "title": "Normalization Quiz",
            "difficulty": "medium",
            "questions": [
                {
                    "question": "What is the purpose of normalization?",
                    "answer": "To reduce data redundancy.",
                    "explanation": "Normalization organizes data to reduce unnecessary duplication.",
                    "source_reference": "DBMS.pdf, page 10"
                },
                {
                    "question": "What does 1NF require?",
                    "answer": "Atomic values.",
                    "explanation": "First Normal Form requires each attribute to contain atomic values.",
                    "source_reference": "DBMS.pdf, page 11"
                }
            ]
        }
        """


def test_generate_quiz():

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

    result = generate_quiz(
        retrieved_chunks=rag_output,
        number_of_questions=2,
        difficulty="medium",
        llm_client=FakeLLM(),
    )

    assert result["title"] == "Normalization Quiz"
    assert result["difficulty"] == "medium"
    assert len(result["questions"]) == 2
    assert result["questions"][0]["answer"] == (
        "To reduce data redundancy."
    )
    assert result["sources"] == ["DBMS.pdf"]