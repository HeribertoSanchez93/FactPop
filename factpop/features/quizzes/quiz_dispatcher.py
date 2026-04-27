from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from factpop.features.quizzes.models import Quiz


@runtime_checkable
class QuizDispatcher(Protocol):
    """Display a quiz popup and wire up submit/skip callbacks."""

    def show_quiz(
        self,
        quiz: Quiz,
        on_submit: Callable[[int], None],
        on_skip: Callable[[], None],
    ) -> None: ...


class NullQuizDispatcher:
    """No-op quiz dispatcher for tests — records calls and stores callbacks."""

    def __init__(self) -> None:
        self.shown_count: int = 0
        self.last_quiz: Quiz | None = None
        self._on_submit: Callable[[int], None] | None = None
        self._on_skip: Callable[[], None] | None = None

    def show_quiz(
        self,
        quiz: Quiz,
        on_submit: Callable[[int], None],
        on_skip: Callable[[], None],
    ) -> None:
        self.shown_count += 1
        self.last_quiz = quiz
        self._on_submit = on_submit
        self._on_skip = on_skip

    def trigger_submit(self, selected_index: int) -> None:
        if self._on_submit is not None:
            self._on_submit(selected_index)

    def trigger_skip(self) -> None:
        if self._on_skip is not None:
            self._on_skip()
