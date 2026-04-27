from __future__ import annotations

from typing import Callable

from factpop.features.history.models import FactRecord


class NullDispatcher:
    """No-op dispatcher for tests and headless environments.

    Records every show_fact() call and stores the callbacks so tests can
    trigger them explicitly via trigger_save() / trigger_show_another() /
    trigger_close().
    """

    def __init__(self) -> None:
        self.shown_count: int = 0
        self.last_record: FactRecord | None = None
        self._on_save: Callable[[], None] | None = None
        self._on_show_another: Callable[[], None] | None = None

    def show_fact(
        self,
        record: FactRecord,
        on_save: Callable[[], None],
        on_show_another: Callable[[], None],
    ) -> None:
        self.shown_count += 1
        self.last_record = record
        self._on_save = on_save
        self._on_show_another = on_show_another

    def trigger_save(self) -> None:
        """Simulate the user clicking Save."""
        if self._on_save is not None:
            self._on_save()

    def trigger_show_another(self) -> None:
        """Simulate the user clicking Show Another."""
        if self._on_show_another is not None:
            self._on_show_another()

    def trigger_close(self) -> None:
        """Simulate the user clicking Close or the X button (no callbacks)."""
        # Close has no callback — intentionally a no-op
