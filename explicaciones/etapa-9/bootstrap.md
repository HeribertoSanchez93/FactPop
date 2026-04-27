# `factpop/app/bootstrap.py` — Wiring completo

`bootstrap()` es el único lugar donde se instancian y conectan todos los servicios. Al finalizar la Etapa 9, el flujo completo del sistema está conectado.

---

## Cadena de dependencias construida en bootstrap

```
settings_svc  ← TinyDBSettingsRepository(app_config)
history_svc   ← TinyDBFactHistoryRepository(fact_history)
review_svc    ← TinyDBReviewRepository(review_queue)
attempt_repo  ← TinyDBQuizAttemptRepository(quiz_attempts)
topic_svc     ← TinyDBTopicRepository(topics)

llm           ← OpenAICompatibleClient(DotenvSecretStore())

fact_svc      ← FactService(topic_svc, history_svc, llm)
quiz_svc      ← QuizService(history_svc, review_svc, llm, attempt_repo)

popup_state   ← PopupState()
fact_dispatcher ← TkPopupDispatcher (o NullDispatcher si falla)
quiz_dispatcher ← TkQuizDispatcher  (o NullQuizDispatcher si falla)

runner        ← ScheduleRunner()
fact_job      ← make_fact_job(fact_svc, fact_dispatcher, history_svc, popup_state)
quiz_job      ← make_quiz_job(quiz_svc, quiz_dispatcher, popup_state, runner)

_scheduler_service ← SchedulerService(settings_svc, runner, fact_job, quiz_job, SystemClock())
_scheduler_service.start()
```

## Fallback si tkinter falla

```python
try:
    from factpop.features.notifications.tk_popup import TkPopupDispatcher
    fact_dispatcher = TkPopupDispatcher()
except Exception:
    fact_dispatcher = NullDispatcher()
```

Si el display server no está disponible (headless), usa `NullDispatcher`. El scheduler sigue funcionando — solo no muestra popups. Útil para correr FactPop en un servidor remoto o en CI.

## `shutdown()` — limpieza al salir

```python
def shutdown() -> None:
    global _scheduler_service
    if _scheduler_service is not None:
        _scheduler_service.stop()
        _scheduler_service = None
```

Llamado desde `__main__.py` en el bloque `finally`. Detiene el scheduler thread correctamente antes de cerrar la DB y el proceso.
