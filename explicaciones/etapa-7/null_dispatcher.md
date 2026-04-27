# `factpop/features/notifications/null.py` — `NullDispatcher`

**Propósito:** Implementación fake del `NotificationDispatcher` para tests. No abre ninguna ventana ni llama a ninguna API del SO. Registra qué se le mostró y guarda los callbacks para que los tests puedan dispararlos manualmente.

```python
class NullDispatcher:
    def __init__(self) -> None:
        self.shown_count: int = 0
        self.last_record: FactRecord | None = None
        self._on_save: Callable | None = None
        self._on_show_another: Callable | None = None
```

**Uso en tests:**

```python
# 1. Verificar que el dispatcher fue llamado con el record correcto
disp = NullDispatcher()
runner.invoke(app, ["facts", "generate", "--show"])
assert disp.shown_count == 1
assert disp.last_record.topic == "Java"

# 2. Simular que el usuario hace click en Save
disp.trigger_save()  # llama on_save()
# Verificar efecto:
history = runner.invoke(app, ["history", "list", "--saved-only"])
assert "Java" in history.output

# 3. Simular que el usuario hace click en Close
disp.trigger_close()  # no llama ningún callback
# Verificar que NO se guardó:
history = runner.invoke(app, ["history", "list", "--saved-only"])
assert "Java" not in history.output
```

**`trigger_save()` vs `trigger_show_another()` vs `trigger_close()`**

Cada método simula una acción diferente del usuario:
- `trigger_save()` → llama `_on_save` (si fue registrado)
- `trigger_show_another()` → llama `_on_show_another`
- `trigger_close()` → no hace nada (Close no tiene callback)

Si se llama a `show_fact()` varias veces, `trigger_save()` siempre usa el callback del último `show_fact()` — porque el test solo puede interactuar con una ventana a la vez.

**Este es el mismo patrón que `FakeLLMClient` (Stage 4):**

| FakeLLMClient | NullDispatcher |
|---|---|
| `call_count` | `shown_count` |
| `last_prompt` | `last_record` |
| `error=` para simular fallas | `trigger_close()` para simular no-acción |
| Inyectado vía `_build_llm` monkeypatch | Inyectado vía `_build_dispatcher` monkeypatch |
