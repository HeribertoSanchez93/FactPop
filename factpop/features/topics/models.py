from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Topic:
    id: str
    name: str
    active: bool = field(default=True)
