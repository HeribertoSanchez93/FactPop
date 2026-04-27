from __future__ import annotations

import uuid

from tinydb.table import Table

from factpop.features.topics.models import Topic


class TinyDBTopicRepository:
    def __init__(self, table: Table) -> None:
        self._table = table

    def create(self, name: str) -> Topic:
        topic_id = str(uuid.uuid4())
        self._table.insert({"id": topic_id, "name": name, "active": True})
        return Topic(id=topic_id, name=name, active=True)

    def find_by_name(self, name: str) -> Topic | None:
        needle = name.lower()
        for row in self._table.all():
            if row["name"].lower() == needle:
                return self._to_model(row)
        return None

    def find_by_id(self, topic_id: str) -> Topic | None:
        for row in self._table.all():
            if row["id"] == topic_id:
                return self._to_model(row)
        return None

    def list_all(self) -> list[Topic]:
        return [self._to_model(row) for row in self._table.all()]

    def list_active(self) -> list[Topic]:
        return [self._to_model(row) for row in self._table.all() if row["active"]]

    def save(self, topic: Topic) -> None:
        self._table.update(
            {"name": topic.name, "active": topic.active},
            cond=lambda row: row["id"] == topic.id,
        )

    def delete(self, topic_id: str) -> None:
        self._table.remove(cond=lambda row: row["id"] == topic_id)

    @staticmethod
    def _to_model(row: dict) -> Topic:
        return Topic(id=row["id"], name=row["name"], active=row["active"])
