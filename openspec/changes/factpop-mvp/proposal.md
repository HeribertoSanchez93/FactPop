## Why

Developers and learners who want to absorb knowledge passively while working lack a frictionless tool that integrates into their daily workflow — existing solutions require manual engagement or are too rigid. FactPop solves this by running silently in the background and surfacing bite-sized, LLM-generated learning facts as native OS popups at user-defined intervals, with optional quizzes to reinforce retention.

## What Changes

- Introduce a local background application (FactPop) that did not previously exist
- New topic management: users define, activate, and deactivate learning topics
- New schedule configuration: users set specific popup times or enable random-interval mode
- New LLM-powered fact generation: dynamic facts generated via OpenAI-compatible API (no static content)
- New popup display system: native OS notifications showing topic, fact, optional example, and actions
- New fact history storage: all shown facts persisted locally in SQLite
- New quiz system: periodic quizzes based on previously shown facts, with incorrect-answer tracking and re-queuing

## Capabilities

### New Capabilities

- `topic-management`: Create, list, activate, and deactivate user-defined learning topics
- `schedule-configuration`: Configure specific popup times and random-interval mode; enable/disable quizzes
- `fact-generation`: Generate dynamic learning facts using an OpenAI-compatible LLM API, with the LLM client as a replaceable adapter
- `popup-display`: Display native OS popup notifications with fact content and interactive actions (show another, save, close)
- `fact-history`: Persist all shown facts locally; serve as the source of truth for quiz generation
- `quiz-system`: Generate multiple-choice quizzes from fact history, track incorrect answers, and re-queue them for future review

### Modified Capabilities

## Impact

- New standalone local application (no existing codebase affected)
- Requires local SQLite database for topics, configuration, fact history, quiz results
- Requires OS-level notification integration (Windows/macOS/Linux)
- Requires outbound HTTP calls to an OpenAI-compatible API endpoint
- Background scheduler process must start on system login or on-demand
