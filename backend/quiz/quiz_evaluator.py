def evaluate_quiz(
    questions: list[dict],
    user_answers: list[str | None],
) -> dict:
    """
    Evaluate a student's quiz answers.

    Args:
        questions: Quiz questions containing correct answers.
        user_answers: Student's answers in the same order as questions.

    Returns:
        Dictionary containing score, results, and weak topics.
    """

    if not isinstance(questions, list):
        raise ValueError("questions must be a list.")

    if not isinstance(user_answers, list):
        raise ValueError("user_answers must be a list.")

    if len(questions) != len(user_answers):
        raise ValueError(
            "Number of user answers must match number of questions."
        )

    total_questions = len(questions)
    correct_count = 0
    results = []

    for index, (question, user_answer) in enumerate(
        zip(questions, user_answers)
    ):
        if not isinstance(question, dict):
            raise ValueError(
                f"Question {index + 1} must be an object."
            )

        if "correct_answer" in question:
            correct_answer = question["correct_answer"]
        elif "answer" in question:
            correct_answer = question["answer"]
        else:
            raise ValueError(
                f"Question {index + 1} has no correct answer."
            )

        is_correct = (
            user_answer is not None
            and str(user_answer).strip().lower()
            == str(correct_answer).strip().lower()
        )

        if is_correct:
            correct_count += 1

        results.append(
            {
                "question_number": index + 1,
                "question": question.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get(
                    "explanation",
                    "",
                ),
                "source_reference": question.get(
                    "source_reference",
                    "",
                ),
            }
        )

    percentage = (
        (correct_count / total_questions) * 100
        if total_questions > 0
        else 0
    )

    return {
        "total_questions": total_questions,
        "correct": correct_count,
        "incorrect": total_questions - correct_count,
        "score": correct_count,
        "percentage": round(percentage, 2),
        "results": results,
    }