# Etapa 7 — Popup Display

| Archivo | Explicación |
|---|---|
| `factpop/features/notifications/dispatcher.py` | [dispatcher.md](dispatcher.md) |
| `factpop/features/notifications/null.py` | [null_dispatcher.md](null_dispatcher.md) |
| `factpop/features/notifications/utils.py` | [utils.md](utils.md) |
| `factpop/features/notifications/tk_popup.py` | [tk_popup.md](tk_popup.md) |
| `factpop/features/notifications/plyer_toast.py` | [plyer_toast.md](plyer_toast.md) |
| `factpop/app/__main__.py` (tray icon) | [tray.md](tray.md) |
| Tests (2 archivos, 20 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/features/notifications/
  dispatcher.py   ← NotificationDispatcher Protocol
  null.py         ← NullDispatcher (tests / headless)
  utils.py        ← truncate_for_toast()
  tk_popup.py     ← TkPopupDispatcher (manual QA only)
  plyer_toast.py  ← send_toast() nudge (manual QA, deferred a Stage 9)

factpop/app/
  __main__.py     ← tray icon pystray + menu (manual QA)

factpop/features/facts/
  cli.py          ← actualizado con --show flag + _build_dispatcher()

tests/unit/features/
  test_notifications.py      ← 14 tests (NullDispatcher + truncation)
  test_facts_cli_show.py     ← 6 tests (--show flag con NullDispatcher)

tests/
  manual-qa.md               ← actualizado con checklist de Stage 7
```

## ¿Por qué TkPopupDispatcher y pystray NO tienen tests automatizados?

El plan (aprobado por el arquitecto) establece explícitamente:
> "No tests automatizados de tkinter/plyer/pystray. Existe `tests/manual-qa.md` con checklist."

Razones técnicas:
1. **tkinter** requiere un display server. En un entorno CI/headless falla al crear `Tk()`.
2. **pystray** requiere un sistema de tray del SO (Windows/macOS/Linux) — no simulable.
3. **plyer** llama a APIs nativas del SO para las notificaciones toast.

Lo que SÍ se puede testear (y se hace):
- El `NullDispatcher` que actúa como "fake" del dispatcher real
- La lógica de callbacks (`on_save`, `on_show_another`)
- La utilidad `truncate_for_toast()`
- El CLI `--show` flag completo (con NullDispatcher vía monkeypatch)

## Flujo del --show flag

```
factpop-cli facts generate --show
    ↓
FactService.generate_and_record() → FactRecord
    ↓
_build_dispatcher() → TkPopupDispatcher (o NullDispatcher en tests)
    ↓
dispatcher.show_fact(record, on_save, on_show_another)
    ↓
  [TkPopupDispatcher]              [NullDispatcher]
  Abre ventana tkinter             Registra la llamada
  Muestra topic + fact + example   Guarda callbacks
  Botones: Save / Show Another / Close
    ↓ usuario hace click
  on_save() → history.mark_saved()
  on_show_another() → genera nuevo fact → show_fact() recursivo
  Close → destruye ventana sin callback
```

## Gate de aceptación

| Check | Método |
|---|---|
| `facts generate --show` invoca dispatcher con record correcto | Automatizado (NullDispatcher) |
| `trigger_save()` llama `on_save` → history marcada | Automatizado |
| `trigger_close()` no llama callbacks | Automatizado |
| Ventana tkinter aparece con topic/fact/botones | Manual QA |
| Botón Save → fact en `--saved-only` | Manual QA |
| Botón Show Another → nueva ventana | Manual QA |
| Tray icon aparece + menu funciona | Manual QA |
| 239 tests totales | Automatizado |
