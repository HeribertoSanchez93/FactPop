from __future__ import annotations

_ELLIPSIS = "..."


def truncate_for_toast(text: str, max_chars: int = 100) -> str:
    """Truncate text to fit in an OS toast notification (max 100 chars by default)."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(_ELLIPSIS)] + _ELLIPSIS
