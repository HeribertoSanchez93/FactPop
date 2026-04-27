# Etapa 9 — Scheduler

| Archivo | Explicación |
|---|---|
| `factpop/shared/scheduler/clock.py` | [clock.md](clock.md) |
| `factpop/shared/scheduler/popup_state.py` | [popup_state.md](popup_state.md) |
| `factpop/shared/scheduler/random_times.py` | [random_times.md](random_times.md) |
| `factpop/shared/scheduler/job_scheduler.py` | [job_scheduler.md](job_scheduler.md) |
| `factpop/shared/scheduler/jobs.py` | [jobs.md](jobs.md) |
| `factpop/shared/scheduler/service.py` | [service.md](service.md) |
| `factpop/shared/scheduler/schedule_runner.py` | [schedule_runner.md](schedule_runner.md) |
| `factpop/features/quizzes/quiz_dispatcher.py` | [quiz_dispatcher.md](quiz_dispatcher.md) |
| `factpop/features/quizzes/tk_window.py` | Manual QA only |
| `factpop/app/bootstrap.py` + `__main__.py` | [bootstrap.md](bootstrap.md) |
| Tests (3 archivos, 38 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/shared/scheduler/
  clock.py           ← Clock Protocol + SystemClock + FrozenClock
  popup_state.py     ← PopupState (flag compartido: popup visible?)
  random_times.py    ← random_times_in_window() utility
  job_scheduler.py   ← JobScheduler Protocol + FakeScheduleRunner (tests)
  jobs.py            ← make_fact_job() + make_quiz_job() factories
  service.py         ← SchedulerService (registra jobs desde config)
  schedule_runner.py ← ScheduleRunner (implementación real con `schedule` lib)

factpop/features/quizzes/
  quiz_dispatcher.py ← QuizDispatcher Protocol + NullQuizDispatcher
  tk_window.py       ← TkQuizDispatcher (manual QA, no automated tests)

factpop/app/
  bootstrap.py       ← crea y conecta todos los servicios + inicia scheduler
  __main__.py        ← llama shutdown() al salir (limpieza del scheduler)
```

## Arquitectura del scheduler

```
main thread: pystray (tray icon)
daemon thread: ScheduleRunner (schedule lib, runs pending jobs every 1s)

Cada segundo en el daemon thread:
  ↓ scheduler.run_pending()
  ↓ si es hora de un fact job:
      fact_job() → generate_and_record() → dispatcher.show_fact()
  ↓ si es hora de un quiz job:
      quiz_job() → si popup_state.is_active() → defer +5min
               → quiz_svc.generate() → quiz_dispatcher.show_quiz()
```

## Gate de aceptación (verificado)

| Check | Método |
|---|---|
| Registro de 2 horarios fijos + random + quiz | Automatizado (FakeScheduleRunner) |
| Jobs dentro de la ventana configurada | Automatizado |
| Quiz deferred cuando popup activo | Automatizado (popup_state.set_active()) |
| Rescheduled job aparece en runner.once_jobs | Automatizado |
| Popup real aparece a la hora configurada | Manual QA |
| Proceso exits limpiamente (scheduler stopped) | Manual QA |
| 342 tests totales | Automatizado |
