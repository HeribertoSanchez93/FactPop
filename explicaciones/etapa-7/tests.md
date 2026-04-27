# Tests de Etapa 7 (TDD) — 20 tests nuevos

## `test_notifications.py` — 14 tests

### NullDispatcher (8 tests)

```python
def test_null_dispatcher_trigger_close_does_not_call_save_or_show_another() -> None:
    disp = NullDispatcher()
    save_calls = []
    show_another_calls = []
    disp.show_fact(
        _make_record(),
        on_save=lambda: save_calls.append(True),
        on_show_another=lambda: show_another_calls.append(True),
    )
    disp.trigger_close()
    assert save_calls == []
    assert show_another_calls == []
```
"Close no tiene callback" — el test verifica que `trigger_close()` NO llama a ninguno de los callbacks registrados. Contraste con `trigger_save()` y `trigger_show_another()` que sí los llaman.

```python
def test_null_dispatcher_trigger_save_only_fires_last_registered_callback() -> None:
    disp = NullDispatcher()
    first_calls = []
    second_calls = []
    disp.show_fact(_make_record(), on_save=lambda: first_calls.append(1), ...)
    disp.show_fact(_make_record(), on_save=lambda: second_calls.append(2), ...)
    disp.trigger_save()
    assert first_calls == []  # overwritten
    assert second_calls == [2]
```
Si `show_fact()` se llama dos veces (ej: "Show Another" abre un segundo popup), `trigger_save()` usa los callbacks del segundo — simula que el usuario interactúa con la ventana más reciente.

### truncate_for_toast (6 tests)

```python
def test_truncate_over_100_chars_adds_ellipsis() -> None:
    text = "a" * 110
    result = truncate_for_toast(text)
    assert len(result) == 100
    assert result.endswith("...")
```

```python
def test_truncate_custom_max_length() -> None:
    text = "Hello World"
    result = truncate_for_toast(text, max_chars=5)
    assert len(result) == 5
    assert result == "He..."
```
El `max_chars=5` test verifica el cálculo: `text[:5-3] + "..."` = `"He" + "..."` = `"He..."` (5 chars). Confirma que la fórmula `max_chars - len("...")` es correcta.

---

## `test_facts_cli_show.py` — 6 tests

Todos usan `monkeypatch.setattr("factpop.features.facts.cli._build_dispatcher", lambda: disp)` para inyectar el `NullDispatcher` en lugar del `TkPopupDispatcher`.

```python
def test_on_save_callback_marks_fact_saved(runner, monkeypatch, tmp_path) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    _patch_llm(monkeypatch, "FACT: Java uses the JVM.")
    disp = _patch_dispatcher(monkeypatch)

    runner.invoke(app, ["facts", "generate", "--show"])
    disp.trigger_save()  # simula usuario haciendo click en Save

    history_result = runner.invoke(app, ["history", "list", "--saved-only"])
    assert "Java" in history_result.output
```

Este test verifica el **flujo completo de integración** entre el dispatcher y el history service:
1. CLI genera el fact y lo pasa al dispatcher con `on_save` = `lambda: history_svc.mark_saved(record.id)`
2. `disp.trigger_save()` ejecuta ese lambda
3. `history list --saved-only` confirma que el fact fue marcado como saved en TinyDB

Es la prueba de que todos los módulos de Stage 7 están correctamente conectados.
