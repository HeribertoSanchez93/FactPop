from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Fact:
    """Parsed LLM response before being persisted as a FactRecord."""
    topic: str
    text: str
    example: str | None = field(default=None)
