from __future__ import annotations

import uuid
from datetime import date, timedelta

from factpop.features.history.models import FactRecord
from factpop.features.reviews.models import ReviewItem
from factpop.features.reviews.repository import TinyDBReviewRepository

_MAX_EXTRA_DAYS = 7


def _today_str(as_of_date: str | None) -> str:
    if as_of_date:
        return as_of_date
    return date.today().isoformat()


def _add_days(date_str: str, days: int) -> str:
    return (date.fromisoformat(date_str) + timedelta(days=days)).isoformat()


class ReviewService:
    def __init__(self, repo: TinyDBReviewRepository) -> None:
        self._repo = repo

    def enqueue(self, fact: FactRecord, as_of_date: str | None = None) -> None:
        """Add a fact to the review queue, or increment its fail count if already queued."""
        existing = self._repo.find_by_fact_id(fact.id)
        today = _today_str(as_of_date)

        if existing is not None and not existing.resolved:
            self.increment_fail(fact.id, as_of_date)
            return

        new_item = ReviewItem(
            id=str(uuid.uuid4()),
            fact_id=fact.id,
            fact_text=fact.text,
            fact_topic=fact.topic,
            next_review_date=_add_days(today, 1),
            fail_count=1,
        )
        self._repo.insert(new_item)

    def increment_fail(self, fact_id: str, as_of_date: str | None = None) -> None:
        """Bump next_review_date by 1 extra day (capped at today + 7)."""
        item = self._repo.find_by_fact_id(fact_id)
        if item is None:
            return
        today = _today_str(as_of_date)
        item.fail_count += 1
        extra_days = min(item.fail_count, _MAX_EXTRA_DAYS)
        item.next_review_date = _add_days(today, extra_days)
        self._repo.update(item)

    def resolve(self, fact_id: str) -> None:
        item = self._repo.find_by_fact_id(fact_id)
        if item is None:
            return
        item.resolved = True
        self._repo.update(item)

    def get_due(self, as_of_date: str | None = None) -> list[ReviewItem]:
        return self._repo.get_due(as_of_date=_today_str(as_of_date))

    def get_pending(self) -> list[ReviewItem]:
        return self._repo.get_pending()
