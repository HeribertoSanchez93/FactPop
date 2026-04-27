## 1. Implementation

- [x] 1.1 Add `import threading` and `import time` to the imports in `factpop/app/__main__.py` (replaced `signal`/`sys` — original SIGINT handler approach did not work because pystray's Win32 message loop blocks signal delivery)
- [x] 1.2 Declare a module-level variable `_icon_ref = None` to hold the pystray icon reference
- [x] 1.3 Add `stop_event: threading.Event` parameter to `_build_tray_icon()`; update `on_quit` to also call `stop_event.set()` so the main thread exits its wait loop
- [x] 1.4 Create `_stop_event = threading.Event()` in `main()` and pass it to `_build_tray_icon()`
- [x] 1.5 Replace `icon.run()` with `icon.run_detached()` (pystray in background thread) + main thread loop `while not _stop_event.is_set(): time.sleep(0.1)` with `except KeyboardInterrupt` to catch Ctrl+C

## 2. Verification

- [x] 2.1 Run the full test suite (`scripts/run_tests.ps1`) — all 359 tests must pass (no regressions)
- [ ] 2.2 Manual QA: start `python -m factpop`, press Ctrl+C in the terminal, verify the tray icon disappears and the process exits cleanly (exit code 0, log shows "FactPop stopped")
- [ ] 2.3 Manual QA: verify tray Quit still works normally (behavior unchanged)
- [ ] 2.4 Manual QA: verify that running `python -m factpop` a second time while a first instance is running shows the "already running" message (lock is released correctly by Ctrl+C shutdown)
