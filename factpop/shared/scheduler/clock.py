from __future__ import annotations

from datetime import date, datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime: ...
    def today(self) -> date: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return date.today()


class FrozenClock:
    """Fixed-time clock for deterministic tests."""

    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed

    def today(self) -> date:
        return self._fixed.date()
