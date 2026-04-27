from __future__ import annotations

import uuid

from tinydb.table import Table

from factpop.features.history.models import FactRecord

_DEFAULT_MAX_SIZE = 500


class TinyDBFactHistoryRepository:
    def __init__(self, table: Table, max_size: int = _DEFAULT_MAX_SIZE) -> None:
        self._table = table
        self._max_size = max_size

    # --- write ---

    def insert(self, record: FactRecord) -> None:
        if self.count() >= self._max_size:
            self._evict_oldest_non_saved()
        self._table.insert(self._to_dict(record))

    def mark_saved(self, record_id: str) -> None:
        self._table.update(
            {"saved": True},
            cond=lambda row: row["id"] == record_id,
        )

    # --- read ---

    def find_by_id(self, record_id: str) -> FactRecord | None:
        for row in self._table.all():
            if row["id"] == record_id:
                return self._to_model(row)
        return None

    def list_recent(
        self,
        topic: str | None = None,
        limit: int = 50,
    ) -> list[FactRecord]:
        rows = self._table.all()
        if topic is not None:
            rows = [r for r in rows if r["topic"] == topic]
        rows.sort(key=lambda r: r["shown_at"], reverse=True)
        return [self._to_model(r) for r in rows[:limit]]

    def count(self) -> int:
        return len(self._table.all())

    # --- internals ---

    def _evict_oldest_non_saved(self) -> None:
        """Delete the oldest non-saved record. No-op if all records are saved."""
        rows = [r for r in self._table.all() if not r["saved"]]
        if not rows:
            return
        oldest = min(rows, key=lambda r: r["shown_at"])
        self._table.remove(cond=lambda row: row["id"] == oldest["id"])

    @staticmethod
    def _to_dict(record: FactRecord) -> dict:
        return {
            "id": record.id,
            "topic": record.topic,
            "text": record.text,
            "shown_at": record.shown_at,
            "example": record.example,
            "saved": record.saved,
        }

    @staticmethod
    def _to_model(row: dict) -> FactRecord:
        return FactRecord(
            id=row["id"],
            topic=row["topic"],
            text=row["text"],
            shown_at=row["shown_at"],
            example=row.get("example"),
            saved=row.get("saved", False),
        )
