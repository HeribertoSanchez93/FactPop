# Tray icon — `factpop/app/__main__.py`

**Sin tests automatizados — ver `tests/manual-qa.md` Stage 7.**

---

## Icono del sistema

```python
img = Image.new("RGB", (64, 64), color="#89b4fa")
draw = ImageDraw.Draw(img)
draw.rectangle([16, 16, 48, 48], fill="#1e1e2e")
```

Icono temporal: cuadrado azul claro con un cuadro oscuro interior. Se reemplazará por un PNG real en Stage 10.

## Menú del tray

```python
menu = pystray.Menu(
    pystray.MenuItem("Show Last Fact", on_show_last_fact),
    pystray.MenuItem("Open Settings", on_open_settings),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Quit", on_quit),
)
```

- **Show Last Fact** → obtiene el fact más reciente de history y lo muestra en `TkPopupDispatcher`. Si no hay facts, muestra un messagebox.
- **Open Settings** → placeholder hasta Stage 10.
- **Quit** → llama `icon.stop()` que termina el `icon.run()` mainloop → control regresa a `main()` → `close_db()` → proceso sale.

## Callbacks de pystray

```python
def on_show_last_fact(_icon, _item):
    ...
def on_quit(icon, _item):
    icon.stop()
```

pystray pasa `(icon, item)` a cada callback. Los prefijamos con `_` cuando no los usamos — convención Python para parámetros intencionalmente ignorados.

## `icon.run()` bloquea el main thread

```python
icon = _build_tray_icon()
icon.run()  # bloquea hasta que icon.stop() es llamado por Quit
```

pystray en Windows **requiere** el main thread. Al hacer `icon.run()`, el main thread queda ocupado manejando eventos del tray. En Stage 9, el scheduler correrá en un **daemon thread** separado, llamando a `root.after(0, ...)` para despachar popups al main thread.

## Fallback a modo consola

```python
except Exception as exc:
    logger.error("Tray icon failed (%s) — fallback to console mode.", exc)
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
```

Si pystray o Pillow fallan (ej: headless server), la app cae back a un loop simple que mantiene el proceso vivo. El scheduler (Stage 9) seguirá funcionando en su daemon thread.
