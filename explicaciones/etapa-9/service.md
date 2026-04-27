# `factpop/shared/scheduler/service.py` — SchedulerService

**Propósito:** Lee la configuración del usuario y registra los jobs correspondientes en el runner. Es el punto de conexión entre "lo que el usuario configuró" y "lo que el scheduler ejecutará".

---

## `setup()` — registro desde config

```python
def setup(self) -> None:
    self._runner.clear_all()          # evita duplicados en re-start
    self._register_specific_times()   # horarios fijos → daily jobs
    self._register_random_slots()     # modo aleatorio → once jobs
    self._register_quiz_job()         # quiz enabled → daily quiz job
```

### Horarios fijos

```python
for time_str in self._settings.get_schedule_times():
    self._runner.add_daily(time_str, self._fact_job, job_id=f"fact-{time_str}")
```

Cada horario fijo se registra como un job diario recurrente. El `job_id` incluye el tiempo para identificarlo en logs.

### Modo aleatorio

```python
config = self._settings.get_random_config()
if config.enabled:
    today = self._clock.today()
    slots = random_times_in_window(config.start, config.end, config.max_per_day, on_date=today)
    for i, dt in enumerate(slots):
        self._runner.add_once_at(dt, self._fact_job, job_id=f"fact-random-{i}")
```

Los slots aleatorios se calculan para el día actual al arrancar. Si el proceso se reinicia al día siguiente, `setup()` genera nuevos slots para ese nuevo día. Esto es suficiente para MVP.

### Quiz job

```python
if self._settings.is_quiz_enabled():
    self._runner.add_daily(_QUIZ_DAILY_TIME, self._quiz_job, job_id="quiz-daily")
```

Un job diario a las 10:00 por defecto. El `quiz_job` internamente decide si tiene suficiente historial para generar un quiz.

---

## `start()` y `stop()`

```python
def start(self) -> None:
    self.setup()
    self._runner.start()  # starts daemon thread

def stop(self) -> None:
    self._runner.stop()   # signals thread to exit and joins
```

`start()` llama `setup()` para re-registrar desde config antes de iniciar el thread. Esto garantiza que al reiniciar el proceso, los jobs siempre reflejan la config actual.

---

## `bootstrap.py` — conecta todo

```python
_scheduler_service = SchedulerService(
    settings=settings_svc,
    runner=runner,
    fact_job=make_fact_job(fact_svc, fact_dispatcher, history_svc, popup_state),
    quiz_job=make_quiz_job(quiz_svc, quiz_dispatcher, popup_state, defer_runner=runner),
    clock=SystemClock(),
)
_scheduler_service.start()
```

El `runner` se pasa tanto al `SchedulerService` (para registrar jobs) como a `make_quiz_job` (para reagendar el quiz cuando está deferred). Es el mismo objeto — cuando el quiz job reagenda, agrega un job directamente al mismo scheduler.
