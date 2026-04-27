## Context

`factpop/app/__main__.py` starts pystray via `icon.run()`, which runs the Win32 message loop on the main thread. On Windows, this loop processes OS messages but does not surface Python's `SIGINT` (Ctrl+C) as a `KeyboardInterrupt` in the normal way. As a result, pressing Ctrl+C in the terminal where the daemon was launched has no effect — the process keeps running.

The current stop paths are:
1. Tray icon → Quit → calls `icon.stop()` → `icon.run()` returns → `finally` block runs shutdown.
2. `taskkill` / Task Manager → abrupt process termination (no clean shutdown).

## Goals / Non-Goals

**Goals:**
- Ctrl+C in the terminal triggers the same clean shutdown sequence as tray Quit.
- No change to end-user behavior — the tray Quit path is untouched.
- No new dependencies.

**Non-Goals:**
- Handling SIGTERM (separate concern, lower priority).
- Making Ctrl+C work when the app is running as a background service without a terminal.
- Changing any behavior of the tray icon, scheduler, or other modules.

## Decisions

### Decision 1: Use `signal.signal(signal.SIGINT, handler)` in `main()`

The handler stores a reference to the `pystray.Icon` instance at module level so it can call `icon.stop()` from the signal context.

```
_icon_ref = None   # module-level

def main():
    ...
    def _handle_sigint(*_):
        if _icon_ref is not None:
            _icon_ref.stop()
        else:
            sys.exit(0)

    signal.signal(signal.SIGINT, _handle_sigint)
    _icon_ref = _build_tray_icon()
    _icon_ref.run()   # blocks until stop() called
```

**Why this over alternatives:**

- **`icon.run_detached()` + `signal` in main thread loop**: More complex; `run_detached()` is less portable across pystray versions.
- **`threading.Event` + `signal`**: Would require restructuring the main loop; overkill for a one-line fix.
- **`icon.run(setup=...)` callback**: pystray's `setup` runs after the icon starts; we would still need the signal handler.

### Decision 2: Fallback to `sys.exit(0)` when no icon

If the tray icon failed to build (pystray unavailable, headless system), the app falls back to a `time.sleep` console loop. In that case `_icon_ref` is `None` and the SIGINT handler calls `sys.exit(0)` directly. The `finally` block in `main()` still executes (`shutdown()`, `close_db()`).

## Risks / Trade-offs

- **[Risk] Signal handler runs in the main thread's message loop** — On Windows, `signal` handlers registered with `signal.signal` are not guaranteed to run immediately inside a C extension's event loop. In practice, pystray's Win32 loop does surface Python signals between message processing cycles, so this works. Mitigation: confirmed in testing; documented as Windows-only behavior.
- **[Risk] `_icon_ref` is a mutable global** — Acceptable: it is written once during `main()` startup and read only in the signal handler. No thread-safety issue for a single-write, single-read pattern.

## Migration Plan

Single-file change: `factpop/app/__main__.py`. No migrations, no data changes. Rollback = revert the file.
