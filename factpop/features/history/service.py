from __future__ import annotations

import uuid
from datetime import datetime

from factpop.features.history.models import FactRecord
from factpop.features.history.repository import TinyDBFactHistoryRepository


class FactHistoryService:
    def __init__(self, repo: TinyDBFactHistoryRepository) -> None:
        self._repo = repo

    def record(
        self,
        topic: str,
        text: str,
        example: str | None = None,
    ) -> FactRecord:
        """Persist a newly shown fact and return the saved record."""
        fact = FactRecord(
            id=str(uuid.uuid4()),
            topic=topic,
            text=text,
            shown_at=datetime.now().isoformat(timespec="seconds"),
            example=example,
            saved=False,
        )
        self._repo.insert(fact)
        return fact

    def mark_saved(self, record_id: str) -> None:
        self._repo.mark_saved(record_id)

    def get_recent(
        self,
        topic: str | None = None,
        limit: int = 50,
    ) -> list[FactRecord]:
        return self._repo.list_recent(topic=topic, limit=limit)

    def count(self) -> int:
        return self._repo.count()
