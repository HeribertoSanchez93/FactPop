# `factpop/features/notifications/utils.py` y `plyer_toast.py`

## `truncate_for_toast(text, max_chars=100)`

```python
def truncate_for_toast(text: str, max_chars: int = 100) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(_ELLIPSIS)] + _ELLIPSIS
```

La spec dice: "el toast SHALL incluir el topic y una versión truncada del fact (max 100 chars)". Esta función garantiza que el mensaje del toast nunca supere 100 caracteres.

`len(_ELLIPSIS)` = 3, así que el texto real es `max_chars - 3` + `"..."` = exactamente `max_chars` chars.

---

## `plyer_toast.send_toast(record) -> bool`

```python
def send_toast(record: FactRecord) -> bool:
    try:
        from plyer import notification
        notification.notify(
            title=f"FactPop — {record.topic}",
            message=truncate_for_toast(record.text),
            app_name="FactPop",
            timeout=6,
        )
        return True
    except Exception as exc:
        logger.warning("OS toast notification failed: %s", exc)
        return False
```

**Retorna `bool`** para indicar si el toast fue enviado. El llamador (Stage 9 scheduler job) puede:
- `True` → toast OK, opcionalmente también mostrar popup tkinter
- `False` → toast falló (Focus Assist, permisos, plataforma), abrir popup tkinter directamente

**`except Exception`** (broad) — justificado porque `plyer` puede lanzar errores específicos de plataforma no documentados. Un fallo de notificación nunca debe crashear la app.

**Integración con Stage 9:** El scheduler job llamará:
```python
toast_ok = send_toast(record)
if not toast_ok:
    dispatcher.show_fact(record, on_save=..., on_show_another=...)
```
