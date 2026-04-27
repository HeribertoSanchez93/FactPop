"""Tests for Clock, PopupState and random_times — all pure logic, no I/O."""
from datetime import date, datetime

import pytest
from freezegun import freeze_time

from factpop.shared.scheduler.clock import FrozenClock, SystemClock
from factpop.shared.scheduler.popup_state import PopupState
from factpop.shared.scheduler.random_times import random_times_in_window


# ── Clock ──────────────────────────────────────────────────────────────────

@freeze_time("2026-04-26T09:30:00")
def test_system_clock_now_returns_current_datetime() -> None:
    clock = SystemClock()
    assert clock.now() == datetime(2026, 4, 26, 9, 30, 0)


@freeze_time("2026-04-26T09:30:00")
def test_system_clock_today_returns_current_date() -> None:
    clock = SystemClock()
    assert clock.today() == date(2026, 4, 26)


def test_frozen_clock_now_returns_fixed_datetime() -> None:
    fixed = datetime(2026, 4, 26, 10, 0, 0)
    clock = FrozenClock(fixed)
    assert clock.now() == fixed


def test_frozen_clock_today_returns_date_portion() -> None:
    fixed = datetime(2026, 4, 26, 10, 0, 0)
    clock = FrozenClock(fixed)
    assert clock.today() == date(2026, 4, 26)


def test_frozen_clock_now_is_stable_across_multiple_calls() -> None:
    fixed = datetime(2026, 4, 26, 10, 0, 0)
    clock = FrozenClock(fixed)
    assert clock.now() == clock.now()


# ── PopupState ──────────────────────────────────────────────────────────────

def test_popup_state_initially_inactive() -> None:
    state = PopupState()
    assert state.is_active() is False


def test_popup_state_set_active() -> None:
    state = PopupState()
    state.set_active()
    assert state.is_active() is True


def test_popup_state_set_inactive_after_active() -> None:
    state = PopupState()
    state.set_active()
    state.set_inactive()
    assert state.is_active() is False


def test_popup_state_set_inactive_when_already_inactive_does_not_raise() -> None:
    state = PopupState()
    state.set_inactive()  # must not raise


# ── random_times_in_window ──────────────────────────────────────────────────

def test_random_times_returns_exact_count() -> None:
    times = random_times_in_window("08:00", "22:00", count=3, on_date=date(2026, 4, 26))
    assert len(times) == 3


def test_random_times_all_within_window() -> None:
    start = datetime(2026, 4, 26, 8, 0)
    end = datetime(2026, 4, 26, 22, 0)
    times = random_times_in_window("08:00", "22:00", count=5, on_date=date(2026, 4, 26))
    for t in times:
        assert start <= t < end


def test_random_times_on_correct_date() -> None:
    times = random_times_in_window("08:00", "22:00", count=2, on_date=date(2026, 4, 26))
    for t in times:
        assert t.date() == date(2026, 4, 26)


def test_random_times_are_distinct() -> None:
    times = random_times_in_window("08:00", "22:00", count=5, on_date=date(2026, 4, 26))
    assert len(set(times)) == len(times)


def test_random_times_count_zero_returns_empty() -> None:
    times = random_times_in_window("08:00", "22:00", count=0, on_date=date(2026, 4, 26))
    assert times == []


def test_random_times_deterministic_with_seed() -> None:
    import random as rng_mod
    rng = rng_mod.Random(42)
    t1 = random_times_in_window("08:00", "22:00", count=3, on_date=date(2026, 4, 26), rng=rng)
    rng2 = rng_mod.Random(42)
    t2 = random_times_in_window("08:00", "22:00", count=3, on_date=date(2026, 4, 26), rng=rng2)
    assert t1 == t2
