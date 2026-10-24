from backend.quiz.quiz_evaluator import evaluate_quiz


def test_evaluate_quiz():

    questions = [
        {
            "question": "What is normalization?",
            "correct_answer": "Reduce data redundancy",
            "explanation": "Normalization reduces unnecessary duplication.",
            "source_reference": "DBMS.pdf, page 10",
        },
        {
            "question": "What does 1NF require?",
            "correct_answer": "Atomic values",
            "explanation": "1NF requires atomic values.",
            "source_reference": "DBMS.pdf, page 11",
        },
        {
            "question": "Which normal form removes transitive dependency?",
            "correct_answer": "3NF",
            "explanation": "3NF removes transitive dependency.",
            "source_reference": "DBMS.pdf, page 12",
        },
    ]

    user_answers = [
        "Reduce data redundancy",
        "Wrong answer",
        "3NF",
    ]

    result = evaluate_quiz(
        questions=questions,
        user_answers=user_answers,
    )

    assert result["total_questions"] == 3
    assert result["correct"] == 2
    assert result["incorrect"] == 1
    assert result["score"] == 2
    assert result["percentage"] == 66.67

    assert result["results"][0]["is_correct"] is True
    assert result["results"][1]["is_correct"] is False
    assert result["results"][2]["is_correct"] is True