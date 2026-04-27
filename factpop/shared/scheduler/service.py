from __future__ import annotations

import logging
from typing import Callable

from factpop.features.settings.service import SettingsService
from factpop.shared.scheduler.clock import Clock
from factpop.shared.scheduler.job_scheduler import JobScheduler
from factpop.shared.scheduler.random_times import random_times_in_window

logger = logging.getLogger(__name__)

_QUIZ_DAILY_TIME = "10:00"


class SchedulerService:
    """Reads config and registers all jobs on the runner.

    Called once at startup (and on re-start) to register:
    - One daily job per configured specific time.
    - N one-off random jobs within the configured window (if random mode is on).
    - One daily quiz job (if quizzes are enabled).
    """

    def __init__(
        self,
        settings: SettingsService,
        runner: JobScheduler,
        fact_job: Callable,
        quiz_job: Callable,
        clock: Clock,
    ) -> None:
        self._settings = settings
        self._runner = runner
        self._fact_job = fact_job
        self._quiz_job = quiz_job
        self._clock = clock

    def setup(self) -> None:
        """Clear all jobs and re-register from current config."""
        self._runner.clear_all()
        self._register_specific_times()
        self._register_random_slots()
        self._register_quiz_job()

    def start(self) -> None:
        self.setup()
        self._runner.start()
        logger.info("Scheduler started.")

    def stop(self) -> None:
        self._runner.stop()
        logger.info("Scheduler stopped.")

    # --- private ---

    def _register_specific_times(self) -> None:
        for time_str in self._settings.get_schedule_times():
            self._runner.add_daily(time_str, self._fact_job, job_id=f"fact-{time_str}")
            logger.debug("Registered daily fact job at %s.", time_str)

    def _register_random_slots(self) -> None:
        config = self._settings.get_random_config()
        if not config.enabled:
            return
        today = self._clock.today()
        slots = random_times_in_window(
            config.start, config.end, config.max_per_day, on_date=today
        )
        for i, dt in enumerate(slots):
            self._runner.add_once_at(dt, self._fact_job, job_id=f"fact-random-{i}")
            logger.debug("Registered random fact job at %s.", dt.strftime("%H:%M"))

    def _register_quiz_job(self) -> None:
        if self._settings.is_quiz_enabled():
            self._runner.add_daily(_QUIZ_DAILY_TIME, self._quiz_job, job_id="quiz-daily")
            logger.debug("Registered daily quiz job at %s.", _QUIZ_DAILY_TIME)
