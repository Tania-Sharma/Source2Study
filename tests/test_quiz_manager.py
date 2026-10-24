from backend.quiz.quiz_manager import QuizManager


def test_quiz_manager():

    quiz = {
        "title": "Normalization Quiz",
        "difficulty": "medium",
        "questions": [
            {
                "question": "What is normalization?",
                "answer": "Reduce data redundancy",
                "explanation": "Normalization reduces redundancy.",
            },
            {
                "question": "What does 1NF require?",
                "answer": "Atomic values",
                "explanation": "1NF requires atomic values.",
            },
        ],
    }

    manager = QuizManager(quiz)

    first_question = manager.start()

    assert first_question["question_number"] == 1
    assert first_question["question"] == "What is normalization?"

    result = manager.submit_answer(
        "Reduce data redundancy"
    )

    assert result["completed"] is False

    second_question = manager.get_current_question()

    assert second_question["question_number"] == 2

    result = manager.submit_answer(
        "Atomic values"
    )

    assert result["completed"] is True

    final_result = manager.finish()

    assert final_result["total_questions"] == 2
    assert final_result["correct"] == 2
    assert final_result["percentage"] == 100.0