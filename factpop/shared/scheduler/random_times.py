from __future__ import annotations

import random as rng_module
from datetime import date, datetime, timedelta


def random_times_in_window(
    start: str,
    end: str,
    count: int,
    on_date: date,
    rng: rng_module.Random | None = None,
) -> list[datetime]:
    """Generate `count` distinct random datetimes within [start, end) on on_date.

    Args:
        start:   Window start in HH:MM format (e.g. "08:00").
        end:     Window end in HH:MM format (e.g. "22:00").
        count:   Number of times to generate.
        on_date: The date on which all times fall.
        rng:     Optional seeded Random instance (for deterministic tests).
    """
    if count == 0:
        return []

    if rng is None:
        rng = rng_module.Random()

    sh, sm = int(start[:2]), int(start[3:])
    eh, em = int(end[:2]), int(end[3:])

    window_start = datetime(on_date.year, on_date.month, on_date.day, sh, sm)
    window_end = datetime(on_date.year, on_date.month, on_date.day, eh, em)
    total_seconds = int((window_end - window_start).total_seconds())

    chosen_seconds: set[int] = set()
    while len(chosen_seconds) < count:
        chosen_seconds.add(rng.randint(0, total_seconds - 1))

    return sorted(window_start + timedelta(seconds=s) for s in chosen_seconds)
