from backend.quiz.quiz_evaluator import evaluate_quiz


class QuizManager:
    """
    Manage the lifecycle of a quiz.

    Flow:
        Start quiz
        → Get current question
        → Submit answer
        → Move to next question
        → Finish quiz
        → Get final result
    """

    def __init__(self, quiz: dict):
        if not isinstance(quiz, dict):
            raise ValueError("quiz must be a dictionary.")

        questions = quiz.get("questions")

        if not isinstance(questions, list):
            raise ValueError(
                "quiz must contain a questions list."
            )

        if not questions:
            raise ValueError(
                "quiz must contain at least one question."
            )

        self.quiz = quiz
        self.questions = questions
        self.current_index = 0
        self.user_answers = []
        self.started = False
        self.finished = False

    def start(self) -> dict:
        """Start the quiz and return the first question."""

        if self.finished:
            raise ValueError("Quiz has already been finished.")

        self.started = True

        return self.get_current_question()

    def get_current_question(self) -> dict:
        """Return the current question without revealing the answer."""

        if not self.started:
            raise ValueError("Quiz has not been started.")

        if self.finished:
            raise ValueError("Quiz has already been finished.")

        if self.current_index >= len(self.questions):
            raise ValueError("No more questions available.")

        question = self.questions[self.current_index]

        safe_question = {
            "question_number": self.current_index + 1,
            "total_questions": len(self.questions),
            "question": question.get("question", ""),
        }

        if "options" in question:
            safe_question["options"] = question["options"]

        return safe_question

    def submit_answer(self, answer: str | None) -> dict:
        """
        Submit the answer for the current question.

        The answer is stored and the manager moves to the next question.
        """

        if not self.started:
            raise ValueError("Quiz has not been started.")

        if self.finished:
            raise ValueError("Quiz has already been finished.")

        self.user_answers.append(answer)

        self.current_index += 1

        if self.current_index >= len(self.questions):
            return {
                "message": "All questions answered. Quiz can be finished.",
                "completed": True,
            }

        return {
            "message": "Answer submitted successfully.",
            "completed": False,
            "next_question": self.get_current_question(),
        }

    def get_progress(self) -> dict:
        """Return the student's current quiz progress."""

        return {
            "answered": len(self.user_answers),
            "total": len(self.questions),
            "remaining": len(self.questions)
            - len(self.user_answers),
        }

    def finish(self) -> dict:
        """Finish the quiz and calculate the final result."""

        if not self.started:
            raise ValueError("Quiz has not been started.")

        if self.finished:
            raise ValueError("Quiz has already been finished.")

        if len(self.user_answers) != len(self.questions):
            raise ValueError(
                "All questions must be answered before finishing."
            )

        result = evaluate_quiz(
            questions=self.questions,
            user_answers=self.user_answers,
        )

        self.finished = True

        return result