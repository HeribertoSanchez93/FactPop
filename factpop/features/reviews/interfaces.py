from __future__ import annotations

from typing import Protocol, runtime_checkable

from factpop.features.history.models import FactRecord
from factpop.features.reviews.models import ReviewItem


@runtime_checkable
class ReviewScheduler(Protocol):
    """Interface consumed by QuizService for review queue operations."""

    def enqueue(self, fact: FactRecord, as_of_date: str | None = None) -> None: ...
    def increment_fail(self, fact_id: str, as_of_date: str | None = None) -> None: ...
    def resolve(self, fact_id: str) -> None: ...
    def get_due(self, as_of_date: str | None = None) -> list[ReviewItem]: ...
    def get_pending(self) -> list[ReviewItem]: ...
