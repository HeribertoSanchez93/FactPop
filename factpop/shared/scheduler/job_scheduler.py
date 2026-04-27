from __future__ import annotations

from datetime import datetime
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class JobScheduler(Protocol):
    """Minimal interface for scheduling recurring and one-off jobs."""

    def add_daily(self, time_str: str, callback: Callable, job_id: str = "") -> None: ...
    def add_once_at(self, run_at: datetime, callback: Callable, job_id: str = "") -> None: ...
    def clear_all(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...


class FakeScheduleRunner:
    """In-memory job scheduler for tests — records registrations without scheduling."""

    def __init__(self) -> None:
        # Each entry: (time_str, callback, job_id)
        self.daily_jobs: list[tuple[str, Callable, str]] = []
        # Each entry: (run_at, callback, job_id)
        self.once_jobs: list[tuple[datetime, Callable, str]] = []
        self.started: bool = False
        self.stopped: bool = False

    def add_daily(self, time_str: str, callback: Callable, job_id: str = "") -> None:
        self.daily_jobs.append((time_str, callback, job_id))

    def add_once_at(self, run_at: datetime, callback: Callable, job_id: str = "") -> None:
        self.once_jobs.append((run_at, callback, job_id))

    def clear_all(self) -> None:
        self.daily_jobs.clear()
        self.once_jobs.clear()

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True
