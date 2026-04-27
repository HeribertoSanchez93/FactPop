## Why

When `python -m factpop` is run from a terminal, pressing Ctrl+C does not stop the process because pystray's Win32 message loop on the main thread blocks the SIGINT signal. The only way to stop the daemon is via the tray icon's Quit option or Task Manager — which is acceptable for end users but is a friction point for developers running the app during development and testing.

## What Changes

- Register a `signal.SIGINT` handler in `factpop/app/__main__.py` that calls `icon.stop()` when Ctrl+C is pressed, enabling clean shutdown from the terminal.
- Keep a module-level reference to the tray icon so the SIGINT handler can reach it.
- The handler must also guard against the case where the tray icon failed to initialize (fallback console mode), calling `sys.exit(0)` instead.

## Capabilities

### New Capabilities

- `graceful-terminal-shutdown`: The daemon process responds to SIGINT (Ctrl+C) by stopping the tray icon and triggering the existing shutdown sequence (scheduler stop, DB close, lock release).

### Modified Capabilities

## Impact

- Only `factpop/app/__main__.py` is modified — no other modules, services, tests, or CLI commands are affected.
- No new dependencies introduced (`signal` and `sys` are Python stdlib).
- Existing `on_quit` tray handler behavior is unchanged; Ctrl+C becomes an alternative path to the same shutdown sequence.
