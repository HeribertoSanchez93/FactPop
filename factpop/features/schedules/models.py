from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RandomModeConfig:
    enabled: bool = field(default=False)
    start: str = field(default="08:00")
    end: str = field(default="22:00")
    max_per_day: int = field(default=3)
