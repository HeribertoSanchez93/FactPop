from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FactRecord:
    id: str
    topic: str
    text: str
    shown_at: str          # ISO 8601 timestamp, e.g. "2026-04-25T10:00:00"
    example: str | None = field(default=None)
    saved: bool = field(default=False)
