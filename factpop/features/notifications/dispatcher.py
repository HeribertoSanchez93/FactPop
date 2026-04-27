from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from factpop.features.history.models import FactRecord


@runtime_checkable
class NotificationDispatcher(Protocol):
    """Display a fact popup and wire up user action callbacks.

    Implementations:
      - TkPopupDispatcher: real tkinter window (production)
      - NullDispatcher: records calls without showing UI (tests / headless)
    """

    def show_fact(
        self,
        record: FactRecord,
        on_save: Callable[[], None],
        on_show_another: Callable[[], None],
    ) -> None:
        """Show the fact popup.

        on_save          -- called when the user clicks Save
        on_show_another  -- called when the user clicks Show Another
        Close / X button -- dismisses with no callback
        """
        ...
