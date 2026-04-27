## ADDED Requirements

### Requirement: System selects a random active topic for each popup
The system SHALL randomly select one active topic each time a popup is triggered. All active topics SHALL have an equal probability of selection. If no active topics exist, the system SHALL skip the popup and log a warning.

#### Scenario: Random topic selection with multiple active topics
- **WHEN** a popup is triggered and multiple active topics exist
- **THEN** the system selects one topic at random with uniform distribution

#### Scenario: No active topics available
- **WHEN** a popup is triggered but no active topics exist
- **THEN** the system skips popup generation, logs a warning, and does not call the LLM

### Requirement: System generates a learning fact via LLM
The system SHALL call an OpenAI-compatible LLM API to generate a short, useful learning fact for the selected topic. The prompt SHALL instruct the LLM to produce: a one-sentence fact, an optional brief code or conceptual example, and to keep the response concise (under 150 words).

#### Scenario: Successful fact generation
- **WHEN** the system calls the LLM with a topic and the API responds successfully
- **THEN** the system receives a fact string (and optional example) and proceeds to display the popup

#### Scenario: LLM API timeout or error
- **WHEN** the LLM API call fails (timeout, network error, or non-2xx response)
- **THEN** the system logs the error, skips the popup for this interval, and does NOT retry in the same interval

#### Scenario: LLM response is empty or malformed
- **WHEN** the LLM returns an empty string or a response that cannot be parsed as a fact
- **THEN** the system logs the issue and skips the popup; no empty popup is shown

### Requirement: LLM client is a replaceable adapter
The fact generation module SHALL depend on a `LLMClient` interface with a single `generate(prompt: str) -> str` method. The `OpenAILLMClient` implementation SHALL be the default. Swapping providers SHALL require only substituting the implementation, not modifying content generation logic.

#### Scenario: Default OpenAI-compatible client in use
- **WHEN** the system is configured with an API key and base URL
- **THEN** all fact generation calls go through the `OpenAILLMClient` adapter using those credentials

#### Scenario: Alternative LLM adapter injected
- **WHEN** a different `LLMClient` implementation is injected into the content module
- **THEN** the content generation logic operates identically without code changes

### Requirement: Generated fact is unique relative to recent history
The system SHALL avoid repeating facts shown in the last N facts for the same topic (configurable, default N=10). If uniqueness cannot be guaranteed after one retry, the system SHALL proceed with the generated fact.

#### Scenario: Fact similar to recent history
- **WHEN** the generated fact is a near-duplicate of a recent fact for the same topic
- **THEN** the system requests one additional generation attempt; if the second attempt is also similar, it proceeds and shows the fact

#### Scenario: No recent history for topic
- **WHEN** no prior facts exist for the selected topic
- **THEN** the system generates without any uniqueness constraint
