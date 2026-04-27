from __future__ import annotations

from factpop.features.schedules.models import RandomModeConfig
from factpop.features.settings.repository import TinyDBSettingsRepository

_KEY_SCHEDULE_TIMES = "schedule_times"
_KEY_QUIZ_ENABLED = "quiz_enabled"
_KEY_RANDOM_ENABLED = "random_enabled"
_KEY_RANDOM_START = "random_start"
_KEY_RANDOM_END = "random_end"
_KEY_RANDOM_MAX = "random_max_per_day"


class SettingsService:
    def __init__(self, repo: TinyDBSettingsRepository) -> None:
        self._repo = repo

    # --- schedule times ---

    def get_schedule_times(self) -> list[str]:
        return self._repo.get(_KEY_SCHEDULE_TIMES, default=[])

    def set_schedule_times(self, times: list[str]) -> None:
        self._repo.set(_KEY_SCHEDULE_TIMES, times)

    # --- quiz ---

    def is_quiz_enabled(self) -> bool:
        return self._repo.get(_KEY_QUIZ_ENABLED, default=True)

    def set_quiz_enabled(self, enabled: bool) -> None:
        self._repo.set(_KEY_QUIZ_ENABLED, enabled)

    # --- random mode ---

    def get_random_config(self) -> RandomModeConfig:
        return RandomModeConfig(
            enabled=self._repo.get(_KEY_RANDOM_ENABLED, default=False),
            start=self._repo.get(_KEY_RANDOM_START, default="08:00"),
            end=self._repo.get(_KEY_RANDOM_END, default="22:00"),
            max_per_day=self._repo.get(_KEY_RANDOM_MAX, default=3),
        )

    def set_random_config(self, config: RandomModeConfig) -> None:
        self._repo.set(_KEY_RANDOM_ENABLED, config.enabled)
        self._repo.set(_KEY_RANDOM_START, config.start)
        self._repo.set(_KEY_RANDOM_END, config.end)
        self._repo.set(_KEY_RANDOM_MAX, config.max_per_day)
