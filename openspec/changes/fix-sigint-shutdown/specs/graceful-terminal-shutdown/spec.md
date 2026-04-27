## ADDED Requirements

### Requirement: Daemon responds to Ctrl+C with clean shutdown
The system SHALL register a SIGINT signal handler at startup so that pressing Ctrl+C in the terminal where `python -m factpop` was launched triggers the same clean shutdown sequence as selecting Quit from the tray icon. The shutdown SHALL stop the scheduler, close the database, and release the instance lock before the process exits.

#### Scenario: Ctrl+C stops the running daemon cleanly
- **WHEN** the user presses Ctrl+C in the terminal while the daemon is running with the tray icon active
- **THEN** the tray icon disappears, the scheduler thread stops, the database is closed, the instance lock is released, and the process exits with code 0

#### Scenario: Ctrl+C works even when tray icon failed to initialize
- **WHEN** the user presses Ctrl+C while the daemon is running in fallback console mode (pystray unavailable)
- **THEN** the process exits with code 0 and the shutdown sequence (scheduler stop, DB close, lock release) still executes via the existing finally block

#### Scenario: Tray Quit behavior is unchanged
- **WHEN** the user selects Quit from the tray icon context menu
- **THEN** the behavior is identical to before this change: tray icon disappears, clean shutdown completes, process exits

### Requirement: Shutdown sequence is idempotent
The system SHALL ensure that calling shutdown via Ctrl+C or via tray Quit does not cause errors if either path is invoked. A second signal or a Quit click after shutdown has already started SHALL not raise exceptions or produce error log entries.

#### Scenario: Only one shutdown is triggered regardless of method used
- **WHEN** Ctrl+C is pressed while the shutdown sequence initiated by tray Quit is already in progress
- **THEN** no additional shutdown calls are made and no errors are logged
