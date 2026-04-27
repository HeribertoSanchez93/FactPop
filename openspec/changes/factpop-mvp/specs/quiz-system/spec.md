## ADDED Requirements

### Requirement: System generates quizzes from fact history
When quizzes are enabled, the system SHALL periodically generate a multiple-choice quiz question based on a fact from the user's history. The quiz SHALL be grounded exclusively in previously shown facts — the LLM SHALL NOT introduce information not present in the source fact. Each quiz SHALL have exactly 4 answer options (1 correct, 3 distractors).

#### Scenario: Quiz generated from recent fact
- **WHEN** a quiz trigger fires and fact history contains at least 3 facts
- **THEN** the system selects a fact from history, calls the LLM to generate a 4-option question, and displays the quiz popup

#### Scenario: Insufficient history for quiz
- **WHEN** a quiz trigger fires but fewer than 3 facts exist in history
- **THEN** the system skips quiz generation, logs the reason, and does not display a quiz popup

#### Scenario: Quiz prioritizes review-queue items
- **WHEN** a quiz trigger fires and the review queue contains items due today or earlier
- **THEN** the system uses a fact from the review queue as the quiz source instead of a random recent fact

### Requirement: System triggers quizzes at random intervals
When quizzes are enabled, the system SHALL trigger quizzes at random times that are separate from the regular fact popup schedule. The quiz frequency SHALL be configurable (default: 1–2 quizzes per day). Quizzes SHALL NOT interrupt an active fact popup.

#### Scenario: Quiz fires at random time
- **WHEN** the scheduler determines it is time for a quiz
- **THEN** the quiz popup appears independently of any fact popup schedule

#### Scenario: No quiz while fact popup is active
- **WHEN** a quiz trigger fires while a fact popup window is currently open
- **THEN** the quiz is deferred by a short interval (e.g., 5 minutes)

### Requirement: User answers a quiz question
The quiz popup SHALL display: the source fact (for context), the question, and 4 labeled answer options. The user SHALL be able to select one option and submit. The popup SHALL also allow the user to skip the quiz.

#### Scenario: User selects correct answer
- **WHEN** the user selects the correct answer and submits
- **THEN** the system shows a "Correct!" confirmation, records the attempt as correct, and closes the popup

#### Scenario: User selects incorrect answer
- **WHEN** the user selects an incorrect answer and submits
- **THEN** the system shows the correct answer with a brief explanation, records the attempt as incorrect, adds the fact to the review queue, and closes the popup

#### Scenario: User skips the quiz
- **WHEN** the user clicks "Skip" on the quiz popup
- **THEN** the popup closes with no attempt recorded; the fact is NOT added to the review queue

### Requirement: Incorrect answers are re-queued for future review
The system SHALL maintain a review queue. When the user answers a quiz question incorrectly, the associated fact SHALL be added to the review queue with a `next_review_date` of current date + 1 day. Facts in the review queue SHALL be prioritized as quiz sources when their `next_review_date` is today or earlier.

#### Scenario: Incorrect answer added to review queue
- **WHEN** the user answers a question incorrectly
- **THEN** a review queue entry is created for the source fact with next_review_date = today + 1 day

#### Scenario: Review queue item used in future quiz
- **WHEN** a quiz trigger fires on or after a review item's next_review_date
- **THEN** that fact is selected as the quiz source

#### Scenario: Correct answer on a review-queue item
- **WHEN** the user correctly answers a question that originated from the review queue
- **THEN** the review queue entry is marked as resolved and removed from future quiz selection

#### Scenario: Multiple incorrect answers for the same fact
- **WHEN** the user answers the same fact's quiz incorrectly more than once
- **THEN** the review queue entry's next_review_date is extended by an additional day per incorrect attempt (max +7 days), allowing future extensibility toward spaced repetition

### Requirement: Quiz attempt history is persisted
The system SHALL store all quiz attempts with: fact ID, question text, selected answer, correct answer, whether the answer was correct, and timestamp. This data SHALL be available for future analytics or spaced repetition upgrades.

#### Scenario: Quiz attempt stored after submission
- **WHEN** the user submits a quiz answer (correct or incorrect)
- **THEN** a quiz attempt record is written to the quiz_attempts table with all required fields

#### Scenario: Quiz attempt not stored for skipped quizzes
- **WHEN** the user skips a quiz
- **THEN** no attempt record is written
