## ADDED Requirements

### Requirement: User can configure specific popup times
The system SHALL allow the user to define a list of specific daily times (HH:MM, 24-hour format) at which popup notifications will be triggered. The system SHALL schedule one popup per configured time each day.

#### Scenario: Add a valid specific time
- **WHEN** the user adds a time in HH:MM format (e.g., "09:00")
- **THEN** the system saves the time and schedules a daily popup at that time

#### Scenario: Reject invalid time format
- **WHEN** the user provides a time string that does not match HH:MM or is outside 00:00–23:59
- **THEN** the system rejects the input with a validation error

#### Scenario: Remove a specific time
- **WHEN** the user removes a previously configured time
- **THEN** the system removes that time and cancels any pending job for it

### Requirement: User can enable random-interval popup mode
The system SHALL support a random-interval mode where popups appear at randomly chosen times within a configurable daily window (start time to end time). In random mode, the system SHALL fire at least one and at most a configurable max number of popups per day, at random intervals within the window.

#### Scenario: Enable random mode
- **WHEN** the user enables random mode with a start time, end time, and max-per-day count
- **THEN** the system schedules popups at random times within the defined window each day

#### Scenario: Disable random mode
- **WHEN** the user disables random mode
- **THEN** the system stops scheduling random-interval popups; specific-time popups (if configured) remain active

#### Scenario: Random mode with no window configured
- **WHEN** random mode is enabled but no start/end time window is set
- **THEN** the system uses a sensible default window (e.g., 08:00–22:00)

### Requirement: User can enable or disable quizzes globally
The system SHALL allow the user to toggle quiz generation on or off globally. When quizzes are disabled, no quiz popups SHALL be generated regardless of other settings.

#### Scenario: Disable quizzes
- **WHEN** the user disables quizzes
- **THEN** the system stops generating quiz popups; fact popups continue unaffected

#### Scenario: Enable quizzes
- **WHEN** the user enables quizzes
- **THEN** the system resumes generating quiz popups according to the quiz schedule

### Requirement: User can configure LLM API connection
The system SHALL allow the user to set the LLM API key and base URL (to support any OpenAI-compatible provider). These settings SHALL be stored locally.

#### Scenario: Save valid API key and base URL
- **WHEN** the user provides a non-empty API key and a valid URL
- **THEN** the system stores them and uses them for all subsequent LLM requests

#### Scenario: Missing API key
- **WHEN** the system attempts to generate a fact but no API key is configured
- **THEN** the system logs an error and skips the popup for that interval without crashing
