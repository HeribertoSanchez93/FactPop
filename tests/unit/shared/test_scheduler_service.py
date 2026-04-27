"""Tests for SchedulerService: verifies correct job registration from config."""
from datetime import date

import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.shared.scheduler.clock import FrozenClock
from factpop.shared.scheduler.job_scheduler import FakeScheduleRunner
from factpop.shared.scheduler.service import SchedulerService
from datetime import datetime


def _make_settings(times=None, random_enabled=False, random_start="08:00",
                   random_end="22:00", random_max=2, quiz_enabled=True) -> SettingsService:
    from factpop.features.schedules.models import RandomModeConfig
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBSettingsRepository(db.table("app_config"))
    svc = SettingsService(repo)
    if times:
        svc.set_schedule_times(times)
    if random_enabled:
        svc.set_random_config(RandomModeConfig(
            enabled=True, start=random_start, end=random_end, max_per_day=random_max
        ))
    svc.set_quiz_enabled(quiz_enabled)
    return svc


def _make_scheduler(settings: SettingsService, runner: FakeScheduleRunner,
                    clock=None) -> SchedulerService:
    if clock is None:
        clock = FrozenClock(datetime(2026, 4, 26, 9, 0, 0))
    return SchedulerService(
        settings=settings,
        runner=runner,
        fact_job=lambda: None,
        quiz_job=lambda: None,
        clock=clock,
    )


# ── specific times ──────────────────────────────────────────────────────────

def test_setup_registers_one_daily_job_per_specific_time() -> None:
    settings = _make_settings(times=["09:00", "14:00"], quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    fact_daily = [j for j in runner.daily_jobs if "quiz" not in j[2]]
    assert len(fact_daily) == 2


def test_setup_registers_correct_times() -> None:
    settings = _make_settings(times=["09:00", "14:00"], quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    registered_times = [j[0] for j in runner.daily_jobs]
    assert "09:00" in registered_times
    assert "14:00" in registered_times


def test_setup_registers_no_fact_jobs_when_no_times() -> None:
    settings = _make_settings(times=[], quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    assert len(runner.daily_jobs) == 0
    assert len(runner.once_jobs) == 0


# ── random mode ──────────────────────────────────────────────────────────────

def test_setup_registers_random_once_jobs_when_mode_enabled() -> None:
    settings = _make_settings(random_enabled=True, random_max=3, quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    assert len(runner.once_jobs) == 3


def test_setup_random_jobs_all_within_configured_window() -> None:
    settings = _make_settings(
        random_enabled=True, random_start="10:00", random_end="12:00",
        random_max=5, quiz_enabled=False
    )
    runner = FakeScheduleRunner()
    clock = FrozenClock(datetime(2026, 4, 26, 9, 0, 0))
    svc = _make_scheduler(settings, runner, clock=clock)
    svc.setup()
    window_start = datetime(2026, 4, 26, 10, 0)
    window_end = datetime(2026, 4, 26, 12, 0)
    for run_at, _, _ in runner.once_jobs:
        assert window_start <= run_at < window_end


def test_setup_no_random_jobs_when_mode_disabled() -> None:
    settings = _make_settings(random_enabled=False, quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    assert len(runner.once_jobs) == 0


# ── quiz job ─────────────────────────────────────────────────────────────────

def test_setup_registers_quiz_job_when_enabled() -> None:
    settings = _make_settings(quiz_enabled=True)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    quiz_jobs = [j for j in runner.daily_jobs if "quiz" in j[2]]
    assert len(quiz_jobs) >= 1


def test_setup_does_not_register_quiz_job_when_disabled() -> None:
    settings = _make_settings(quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    quiz_jobs = [j for j in runner.daily_jobs if "quiz" in j[2]]
    assert len(quiz_jobs) == 0


# ── clear on re-setup ─────────────────────────────────────────────────────────

def test_setup_clears_previous_jobs_before_registering() -> None:
    settings = _make_settings(times=["09:00"], quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.setup()
    svc.setup()  # second call should not duplicate
    assert len(runner.daily_jobs) == 1


# ── start / stop ──────────────────────────────────────────────────────────────

def test_start_calls_runner_start() -> None:
    settings = _make_settings(quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.start()
    assert runner.started is True


def test_stop_calls_runner_stop() -> None:
    settings = _make_settings(quiz_enabled=False)
    runner = FakeScheduleRunner()
    svc = _make_scheduler(settings, runner)
    svc.start()
    svc.stop()
    assert runner.stopped is True
