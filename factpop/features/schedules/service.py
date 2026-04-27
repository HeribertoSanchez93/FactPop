from __future__ import annotations

import re

from factpop.features.schedules.errors import (
    InvalidTimeFormatError,
    TimeAlreadyExistsError,
    TimeNotFoundError,
)
from factpop.features.schedules.models import RandomModeConfig
from factpop.features.settings.service import SettingsService

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _validate_time(time: str) -> None:
    """Raise InvalidTimeFormatError if time is not a valid HH:MM string."""
    if not _TIME_RE.match(time):
        raise InvalidTimeFormatError(
            f"'{time}' is not a valid time. Use HH:MM format (e.g., 09:00)."
        )
    hh, mm = int(time[:2]), int(time[3:])
    if hh > 23 or mm > 59:
        raise InvalidTimeFormatError(
            f"Invalid time '{time}': hours must be 00-23, minutes 00-59."
        )


class ScheduleService:
    def __init__(self, settings: SettingsService) -> None:
        self._settings = settings

    def add_time(self, time: str) -> None:
        _validate_time(time)
        times = self._settings.get_schedule_times()
        if time in times:
            raise TimeAlreadyExistsError(f"Time '{time}' is already in the schedule.")
        self._settings.set_schedule_times(times + [time])

    def remove_time(self, time: str) -> None:
        times = self._settings.get_schedule_times()
        if time not in times:
            raise TimeNotFoundError(f"Time '{time}' not found in schedule.")
        self._settings.set_schedule_times([t for t in times if t != time])

    def list_times(self) -> list[str]:
        return self._settings.get_schedule_times()

    def enable_random(
        self,
        start: str = "08:00",
        end: str = "22:00",
        max_per_day: int = 3,
    ) -> None:
        _validate_time(start)
        _validate_time(end)
        self._settings.set_random_config(
            RandomModeConfig(enabled=True, start=start, end=end, max_per_day=max_per_day)
        )

    def disable_random(self) -> None:
        current = self._settings.get_random_config()
        self._settings.set_random_config(
            RandomModeConfig(
                enabled=False,
                start=current.start,
                end=current.end,
                max_per_day=current.max_per_day,
            )
        )

    def get_random_config(self) -> RandomModeConfig:
        return self._settings.get_random_config()
