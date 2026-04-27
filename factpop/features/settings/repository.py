from __future__ import annotations

from typing import Any

from tinydb.table import Table


class TinyDBSettingsRepository:
    """Key-value store backed by a TinyDB table.

    Each setting is stored as {"key": <key>, "value": <value>}.
    Calling set() on an existing key overwrites the previous value.
    """

    def __init__(self, table: Table) -> None:
        self._table = table

    def get(self, key: str, default: Any = None) -> Any:
        for row in self._table.all():
            if row["key"] == key:
                return row["value"]
        return default

    def set(self, key: str, value: Any) -> None:
        exists = any(row["key"] == key for row in self._table.all())
        if exists:
            self._table.update({"value": value}, cond=lambda row: row["key"] == key)
        else:
            self._table.insert({"key": key, "value": value})
