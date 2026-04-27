from __future__ import annotations

from tinydb.table import Table

from factpop.features.reviews.models import ReviewItem


class TinyDBReviewRepository:
    def __init__(self, table: Table) -> None:
        self._table = table

    def insert(self, item: ReviewItem) -> None:
        self._table.insert(self._to_dict(item))

    def update(self, item: ReviewItem) -> None:
        self._table.update(
            self._to_dict(item),
            cond=lambda row: row["id"] == item.id,
        )

    def find_by_fact_id(self, fact_id: str) -> ReviewItem | None:
        for row in self._table.all():
            if row["fact_id"] == fact_id:
                return self._to_model(row)
        return None

    def get_due(self, as_of_date: str) -> list[ReviewItem]:
        return [
            self._to_model(r)
            for r in self._table.all()
            if not r["resolved"] and r["next_review_date"] <= as_of_date
        ]

    def get_pending(self) -> list[ReviewItem]:
        return [self._to_model(r) for r in self._table.all() if not r["resolved"]]

    def count_pending(self) -> int:
        return sum(1 for r in self._table.all() if not r["resolved"])

    @staticmethod
    def _to_dict(item: ReviewItem) -> dict:
        return {
            "id": item.id,
            "fact_id": item.fact_id,
            "fact_text": item.fact_text,
            "fact_topic": item.fact_topic,
            "next_review_date": item.next_review_date,
            "fail_count": item.fail_count,
            "resolved": item.resolved,
        }

    @staticmethod
    def _to_model(row: dict) -> ReviewItem:
        return ReviewItem(
            id=row["id"],
            fact_id=row["fact_id"],
            fact_text=row["fact_text"],
            fact_topic=row["fact_topic"],
            next_review_date=row["next_review_date"],
            fail_count=row.get("fail_count", 1),
            resolved=row.get("resolved", False),
        )
