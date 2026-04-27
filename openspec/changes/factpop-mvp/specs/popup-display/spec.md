## ADDED Requirements

### Requirement: System shows a native OS notification for each fact
The system SHALL display a native OS toast/notification for each generated fact. The notification SHALL include the topic name and the first sentence of the fact. The notification SHALL be non-blocking (does not pause the background process).

#### Scenario: Fact notification displayed
- **WHEN** a fact is successfully generated
- **THEN** the system fires a native OS notification showing the topic and a truncated version of the fact (max 100 chars)

#### Scenario: OS notification not supported
- **WHEN** the system cannot display a native OS notification (unsupported platform or permission denied)
- **THEN** the system falls back to displaying the full popup window automatically

### Requirement: User can open a full fact popup window
The system SHALL provide a small popup window (via tkinter or equivalent) that shows the complete fact content. This window SHALL be triggerable from the notification action or from a system tray icon menu.

#### Scenario: Full popup window content
- **WHEN** the full popup window is opened
- **THEN** it displays: topic name, full fact text, optional example (if present), and action buttons

#### Scenario: Popup window is non-modal
- **WHEN** the popup window is open
- **THEN** the user can interact with other applications without closing the popup first

### Requirement: Popup window provides user actions
The popup window SHALL include the following actions:
- **Show Another**: dismiss current fact, generate and display a new fact for a random topic
- **Save**: mark the current fact as saved in history (sets a `saved` flag)
- **Close**: dismiss the popup without any additional action

#### Scenario: User clicks Show Another
- **WHEN** the user clicks "Show Another" in the popup window
- **THEN** the current popup closes and a new fact is generated and displayed immediately

#### Scenario: User clicks Save
- **WHEN** the user clicks "Save"
- **THEN** the fact's `saved` flag is set to true in fact history and the popup closes

#### Scenario: User clicks Close
- **WHEN** the user clicks "Close"
- **THEN** the popup is dismissed; the fact remains in history with `saved = false`

#### Scenario: User closes popup window via OS close button
- **WHEN** the user clicks the window's X button
- **THEN** the popup is dismissed; behavior is identical to clicking "Close"

### Requirement: System tray icon provides persistent access
The application SHALL run with a system tray icon (Windows notification area). The tray icon menu SHALL include: Show Last Fact, Open Settings, and Quit.

#### Scenario: Open settings from tray
- **WHEN** the user selects "Open Settings" from the tray menu
- **THEN** the settings UI opens

#### Scenario: Show last fact from tray
- **WHEN** the user selects "Show Last Fact" from the tray menu
- **THEN** the most recently generated fact is displayed in the popup window; if no fact exists yet, a message says "No facts generated yet"
