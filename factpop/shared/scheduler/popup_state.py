from __future__ import annotations


class PopupState:
    """Shared mutable flag: is a fact or quiz popup currently visible?

    The scheduler's quiz_job checks this before showing a quiz — if a
    fact popup is open, the quiz is deferred by a few minutes.
    """

    def __init__(self) -> None:
        self._active = False

    def set_active(self) -> None:
        self._active = True

    def set_inactive(self) -> None:
        self._active = False

    def is_active(self) -> bool:
        return self._active
