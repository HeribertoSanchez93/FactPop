# Tests de Etapa 9 (TDD) — 38 tests nuevos

## `test_scheduler_utils.py` — 15 tests

### Clock (5 tests)
```python
@freeze_time("2026-04-26T09:30:00")
def test_system_clock_now_returns_current_datetime() -> None:
    assert SystemClock().now() == datetime(2026, 4, 26, 9, 30, 0)

def test_frozen_clock_now_is_stable_across_multiple_calls() -> None:
    clock = FrozenClock(datetime(2026, 4, 26, 10, 0, 0))
    assert clock.now() == clock.now()
```

### PopupState (4 tests)
Verifican el ciclo `set_active() → is_active() → set_inactive()`.

### random_times (6 tests)
```python
def test_random_times_are_distinct() -> None:
    times = random_times_in_window("08:00", "22:00", count=5, on_date=date(2026, 4, 26))
    assert len(set(times)) == len(times)  # all unique

def test_random_times_deterministic_with_seed() -> None:
    rng = random.Random(42)
    t1 = random_times_in_window(..., rng=rng)
    rng2 = random.Random(42)
    t2 = random_times_in_window(..., rng=rng2)
    assert t1 == t2  # same seed → same result
```

---

## `test_scheduler_jobs.py` — 12 tests

### fact_job (6 tests)
```python
def test_fact_job_on_save_callback_marks_fact_saved() -> None:
    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()
    dispatcher.trigger_save()  # simulate user clicking Save
    recent = history_svc.get_recent(limit=1)
    assert recent[0].saved is True
```

### quiz_job (6 tests)
```python
def test_quiz_job_defers_via_runner_when_popup_active() -> None:
    popup_state.set_active()
    fake_runner = FakeScheduleRunner()
    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=fake_runner)
    job()
    assert len(fake_runner.once_jobs) == 1  # deferred
    assert isinstance(fake_runner.once_jobs[0][0], datetime)  # scheduled at a future time
```

---

## `test_scheduler_service.py` — 11 tests

### FakeScheduleRunner
`FakeScheduleRunner` registra en listas qué jobs se pidieron, sin ejecutar nada. Cada entrada tiene `(time_str/datetime, callback, job_id)`.

```python
def test_setup_registers_random_jobs_all_within_configured_window() -> None:
    settings = _make_settings(random_start="10:00", random_end="12:00", random_max=5)
    runner = FakeScheduleRunner()
    svc.setup()
    window_start = datetime(2026, 4, 26, 10, 0)
    window_end = datetime(2026, 4, 26, 12, 0)
    for run_at, _, _ in runner.once_jobs:
        assert window_start <= run_at < window_end

def test_setup_clears_previous_jobs_before_registering() -> None:
    svc.setup()
    svc.setup()  # second call
    assert len(runner.daily_jobs) == 1  # not 2
```

El último test es importante: verifica que `setup()` llama `clear_all()` primero, evitando que al reiniciar el proceso se acumulen jobs duplicados.
