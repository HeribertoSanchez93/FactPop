# `factpop/features/settings/tk_settings.py`

**Sin tests automatizados — ver `tests/manual-qa.md` Stage 10.**

**Propósito:** Ventana de configuración con tres tabs (Topics, Schedule, History). Se abre desde el tray icon "Open Settings".

---

## Estructura de la ventana

```
┌─────────────────────────────────────┐
│ [Topics] [Schedule] [History]       │  ← ttk.Notebook tabs
├─────────────────────────────────────┤
│ (contenido del tab activo)          │
└─────────────────────────────────────┘
```

### Tab Topics
- Listbox con todos los topics (`[active]  Java`, `[inactive]  Kafka`)
- Entry + botón "Add" — llama `topic_svc.create(name)`
- Botón "Toggle Active" — llama `topic_svc.activate/deactivate(name)` con warning si es el último
- Botón "Delete" — confirmación → `topic_svc.delete(name)`

### Tab Schedule
- Listbox de horarios específicos
- Entry + "Add" → `schedule_svc.add_time(t)` con validación
- "Remove" → `schedule_svc.remove_time(t)`
- Checkbox "Random mode" → `schedule_svc.enable_random()` / `disable_random()`
- Checkbox "Enable quizzes" → `settings_svc.set_quiz_enabled(bool)`

### Tab History
- `tk.Text` read-only con los últimos 30 facts (topic, fecha, texto truncado)
- Botón "Refresh" para recargar

---

## `open_settings_window()` — función de entrada

```python
def open_settings_window() -> None:
    db = get_db()
    topic_svc = ...
    settings_svc = ...
    history_svc = ...
    schedule_svc = ScheduleService(settings_svc)

    root = tk.Tk()
    notebook = ttk.Notebook(root)
    _build_topics_tab(notebook, topic_svc)
    _build_schedule_tab(notebook, schedule_svc, settings_svc)
    _build_history_tab(notebook, history_svc)
    root.mainloop()
    root.destroy()
```

Se llama desde `__main__.py` en el callback del tray "Open Settings". Bloquea el tray hasta que la ventana se cierre — esto es aceptable porque la ventana es modal desde la perspectiva del usuario.

---

## Diferencia con `TkPopupDispatcher`

| TkPopupDispatcher | TkSettingsWindow |
|---|---|
| Creada/destruida por cada popup | Una instancia por apertura del usuario |
| Tiene callbacks externos (on_save, on_show_another) | Llama directamente a los servicios |
| Duración: segundos | Duración: hasta que el usuario la cierra |
