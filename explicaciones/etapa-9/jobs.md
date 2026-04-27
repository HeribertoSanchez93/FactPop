# `factpop/shared/scheduler/jobs.py` — make_fact_job y make_quiz_job

## Patrón Factory

Ambas funciones son **factories** — devuelven un callable en vez de ejecutar directamente. Esto permite:
1. Inyectar todas las dependencias en tiempo de construcción (bootstrap)
2. El scheduler solo guarda el callable `job()` sin conocer sus dependencias
3. Tests pueden construir el job con fakes y verificar su comportamiento

---

## `make_fact_job()`

```python
def make_fact_job(fact_svc, dispatcher, history_svc, popup_state) -> Callable:
    def _job() -> None:
        record = fact_svc.generate_and_record()
        if record is None:
            return  # no active topics or LLM error

        popup_state.set_active()
        try:
            dispatcher.show_fact(
                record,
                on_save=lambda: history_svc.mark_saved(record.id),
                on_show_another=lambda: _job(),  # recursivo
            )
        finally:
            popup_state.set_inactive()
    return _job
```

**`popup_state.set_active()` antes de `show_fact()`** — garantiza que el quiz job no interrumpa mientras el popup está visible. El `TkPopupDispatcher.show_fact()` bloquea hasta que la ventana se cierra, por eso el `set_inactive()` en el `finally` ocurre después de que el usuario cierra el popup.

**`on_show_another` llama `_job()` recursivamente** — genera un nuevo fact y abre otra ventana. El `popup_state` vuelve a `active` durante la nueva ventana.

---

## `make_quiz_job()`

```python
def make_quiz_job(quiz_svc, quiz_dispatcher, popup_state, defer_runner, defer_minutes=5) -> Callable:
    def _job() -> None:
        if popup_state.is_active():
            if defer_runner is not None:
                deferred_at = datetime.now() + timedelta(minutes=defer_minutes)
                defer_runner.add_once_at(deferred_at, _job, job_id="quiz-deferred")
            return

        quiz = quiz_svc.generate()
        if quiz is None:
            return

        popup_state.set_active()
        try:
            quiz_dispatcher.show_quiz(quiz,
                on_submit=lambda idx: quiz_svc.grade(quiz, idx),
                on_skip=lambda: quiz_svc.skip(quiz),
            )
        finally:
            popup_state.set_inactive()
    return _job
```

**Quiz deferral:** si `popup_state.is_active()` → el quiz se reagenda `+5min` vía `defer_runner.add_once_at()`. En tests, `defer_runner=None` desactiva el reagendado (verificable con `assert quiz_disp.shown_count == 0`).
