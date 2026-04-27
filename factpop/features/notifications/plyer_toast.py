from __future__ import annotations

import logging

from factpop.features.history.models import FactRecord
from factpop.features.notifications.utils import truncate_for_toast

logger = logging.getLogger(__name__)


def send_toast(record: FactRecord) -> bool:
    """Fire a native OS toast notification for a fact (non-blocking nudge).

    Returns True if the toast was sent successfully, False on failure.
    The caller should fall back to the full popup window on failure.
    """
    try:
        from plyer import notification  # type: ignore[import]

        notification.notify(
            title=f"FactPop — {record.topic}",
            message=truncate_for_toast(record.text),
            app_name="FactPop",
            timeout=6,
        )
        return True
    except Exception as exc:
        logger.warning("OS toast notification failed: %s", exc)
        return False
