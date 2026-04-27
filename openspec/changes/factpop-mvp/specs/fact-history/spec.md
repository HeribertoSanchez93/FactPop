## ADDED Requirements

### Requirement: System persists every shown fact
The system SHALL save every successfully generated and displayed fact to local SQLite storage. Each record SHALL include: topic name, fact text, optional example, timestamp shown, and a `saved` boolean flag (default false).

#### Scenario: Fact saved after display
- **WHEN** a fact is successfully generated and a popup is shown
- **THEN** a record is written to the fact history table with the correct topic, text, timestamp, and saved=false

#### Scenario: Fact not saved if generation failed
- **WHEN** the LLM call fails and no popup is shown
- **THEN** no record is written to fact history

### Requirement: System limits fact history size
The system SHALL enforce a configurable maximum fact history size (default: 500 records). When the limit is reached, the oldest non-saved facts SHALL be deleted first. Saved facts SHALL be retained regardless of the limit.

#### Scenario: History at capacity with non-saved facts
- **WHEN** a new fact is generated and history is at max capacity and at least one non-saved fact exists
- **THEN** the oldest non-saved fact is deleted before inserting the new record

#### Scenario: History at capacity with only saved facts
- **WHEN** a new fact is generated and all existing facts are saved
- **THEN** the system inserts the new fact, temporarily exceeding the limit; no saved facts are deleted

### Requirement: Fact history is accessible for quiz generation
The system SHALL provide a query interface for the quiz module to retrieve recent facts by topic or globally, ordered by recency. Facts that have already been used as a quiz source SHALL be retrievable.

#### Scenario: Query recent facts for a topic
- **WHEN** the quiz module requests the last N facts for a given topic
- **THEN** the system returns up to N fact records ordered by timestamp descending

#### Scenario: Query recent facts across all topics
- **WHEN** the quiz module requests recent facts with no topic filter
- **THEN** the system returns the most recent facts across all topics

### Requirement: User can view fact history
The system SHALL allow the user to browse the fact history, showing facts with their topic, timestamp, and saved status. The view SHALL support filtering by topic and by saved status.

#### Scenario: View all history
- **WHEN** the user opens the history view with no filters
- **THEN** the system displays all facts ordered by most recent first

#### Scenario: Filter history by topic
- **WHEN** the user filters history by a specific topic
- **THEN** only facts for that topic are shown
