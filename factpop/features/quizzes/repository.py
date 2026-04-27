from __future__ import annotations

from tinydb.table import Table

from factpop.features.quizzes.models import QuizAttempt


class TinyDBQuizAttemptRepository:
    def __init__(self, table: Table) -> None:
        self._table = table

    def insert(self, attempt: QuizAttempt) -> None:
        self._table.insert({
            "id": attempt.id,
            "fact_id": attempt.fact_id,
            "question": attempt.question,
            "selected_answer": attempt.selected_answer,
            "correct_answer": attempt.correct_answer,
            "is_correct": attempt.is_correct,
            "attempted_at": attempt.attempted_at,
        })

    def find_by_fact_id(self, fact_id: str) -> list[QuizAttempt]:
        return [
            self._to_model(r)
            for r in self._table.all()
            if r["fact_id"] == fact_id
        ]

    def count(self) -> int:
        return len(self._table.all())

    @staticmethod
    def _to_model(row: dict) -> QuizAttempt:
        return QuizAttempt(
            id=row["id"],
            fact_id=row["fact_id"],
            question=row["question"],
            selected_answer=row["selected_answer"],
            correct_answer=row["correct_answer"],
            is_correct=row["is_correct"],
            attempted_at=row["attempted_at"],
        )
