from backend.quiz.mcq_generator import generate_mcqs


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return """
        {
            "title": "Normalization MCQ Quiz",
            "difficulty": "medium",
            "questions": [
                {
                    "question": "What is the main purpose of normalization?",
                    "options": [
                        "Reduce data redundancy",
                        "Increase data duplication",
                        "Remove all database tables",
                        "Increase storage requirements"
                    ],
                    "correct_answer": "Reduce data redundancy",
                    "explanation": "Normalization reduces unnecessary duplication of data.",
                    "source_reference": "DBMS.pdf, page 10"
                },
                {
                    "question": "What does First Normal Form require?",
                    "options": [
                        "Atomic values",
                        "Duplicate values",
                        "No tables",
                        "Only numeric attributes"
                    ],
                    "correct_answer": "Atomic values",
                    "explanation": "1NF requires attributes to contain atomic values.",
                    "source_reference": "DBMS.pdf, page 11"
                }
            ]
        }
        """


def test_generate_mcqs():

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

    result = generate_mcqs(
        retrieved_chunks=rag_output,
        number_of_questions=2,
        difficulty="medium",
        llm_client=FakeLLM(),
    )

    assert result["title"] == "Normalization MCQ Quiz"
    assert result["difficulty"] == "medium"

    assert len(result["questions"]) == 2

    first_question = result["questions"][0]

    assert len(first_question["options"]) == 4

    assert (
        first_question["correct_answer"]
        in first_question["options"]
    )

    assert result["sources"] == ["DBMS.pdf"]