from __future__ import annotations

from dataclasses import dataclass, field

from factpop.features.history.models import FactRecord


@dataclass
class Quiz:
    source_fact: FactRecord
    question: str
    options: list[str]        # exactly 4
    correct_index: int        # 0–3
    from_review_queue: bool = field(default=False)


@dataclass
class QuizAttempt:
    id: str
    fact_id: str
    question: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    attempted_at: str         # ISO timestamp
