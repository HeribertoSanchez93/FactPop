# `clock.py`, `popup_state.py`, `random_times.py`, `job_scheduler.py`, `schedule_runner.py`

## `clock.py` — Clock Protocol + implementaciones

```python
class Clock(Protocol):
    def now(self) -> datetime: ...
    def today(self) -> date: ...

class SystemClock:   # producción: devuelve datetime.now() y date.today()
class FrozenClock:   # tests: devuelve siempre la misma fecha configurada
```

**¿Por qué abstraer el reloj?**
El `SchedulerService._register_random_slots()` llama `self._clock.today()` para calcular los slots del día. En producción usa `SystemClock`. En tests usa `FrozenClock(datetime(2026, 4, 26, ...))` para obtener resultados determinísticos — sin importar cuándo corre el test.

---

## `popup_state.py` — PopupState

Flag mutable compartido entre el `fact_job` y el `quiz_job`:
```
fact_job: set_active() → [popup visible] → set_inactive()
quiz_job: if is_active() → defer
```

En el daemon, el scheduler corre en un thread separado. El `PopupState` es accedido desde ese thread. Para MVP es aceptable sin lock (booleano, operaciones atómicas en CPython). En el futuro, se puede proteger con `threading.Lock`.

---

## `job_scheduler.py` — JobScheduler Protocol + FakeScheduleRunner

```python
class FakeScheduleRunner:
    daily_jobs: list[tuple[str, Callable, str]]
    once_jobs: list[tuple[datetime, Callable, str]]
    started: bool
    stopped: bool
```

`FakeScheduleRunner` es el "NullDispatcher del scheduler" — registra las llamadas sin ejecutar nada. Permite verificar en tests que `SchedulerService.setup()` registró exactamente los jobs correctos.

---

## `schedule_runner.py` — ScheduleRunner (implementación real)

Envuelve la librería `schedule` con una interfaz limpia:

```python
def add_daily(self, time_str, callback, job_id="") -> None:
    self._scheduler.every().day.at(time_str).do(callback).tag(job_id or time_str)

def add_once_at(self, run_at, callback, job_id="") -> None:
    # Implementado como un job periódico (cada 30s) que cancela cuando pasa la hora
    def _one_shot():
        if datetime.now() >= run_at:
            callback()
            return schedule.CancelJob
    self._scheduler.every(30).seconds.do(_one_shot).tag(tag)
```

**`add_once_at` no tiene soporte nativo en `schedule`** — se simula con un job que verifica si ya pasó la hora y se cancela con `schedule.CancelJob` cuando se ejecuta. Polling cada 30s es suficiente para el nivel de precisión que necesita FactPop.

---

## `quiz_dispatcher.py` — QuizDispatcher Protocol + NullQuizDispatcher

Mismo patrón que `NotificationDispatcher` (Stage 7) pero para quizzes:
```python
class QuizDispatcher(Protocol):
    def show_quiz(self, quiz, on_submit: Callable[[int], None], on_skip: Callable[[], None]) -> None: ...
```

`NullQuizDispatcher` registra el quiz y los callbacks. `trigger_submit(index)` y `trigger_skip()` los disparan desde tests.
