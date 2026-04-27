from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReviewItem:
    id: str
    fact_id: str
    fact_text: str
    fact_topic: str
    next_review_date: str   # ISO date "2026-04-26"
    fail_count: int = field(default=1)
    resolved: bool = field(default=False)
