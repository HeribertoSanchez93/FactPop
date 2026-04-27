## 1. Project Setup

- [ ] 1.1 Initialize Python project structure with the module layout defined in design.md (db, topics, config, llm, content, popup, history, quiz, scheduler, cli)
- [ ] 1.2 Create `requirements.txt` with dependencies: `openai`, `apscheduler`, `plyer`, `pystray`, `Pillow` (tray icon), `tkinter` (stdlib)
- [ ] 1.3 Set up SQLite database initialization script that creates all tables on first run
- [ ] 1.4 Define SQLite schema: `topics`, `app_config`, `fact_history`, `quiz_attempts`, `review_queue` tables
- [ ] 1.5 Create a CLI entry point (`cli/main.py`) that starts the background daemon and system tray icon

## 2. Topic Management

- [ ] 2.1 Implement `topics/repository.py`: CRUD operations for topics (create, list, get by name, set active/inactive, delete)
- [ ] 2.2 Enforce unique topic name constraint (case-insensitive) in the repository
- [ ] 2.3 Implement `topics/service.py`: business logic (reject duplicate names, warn when deactivating last active topic)
- [ ] 2.4 Create settings UI panel for topic management (add, toggle active, delete) using tkinter
- [ ] 2.5 Write tests for topic service: create duplicate, deactivate last active topic, delete with history

## 3. Schedule Configuration

- [ ] 3.1 Implement `config/repository.py`: key-value store for app settings in `app_config` table
- [ ] 3.2 Implement `config/service.py`: get/set for specific times list, random mode flag, random window (start/end), max-per-day, quiz enabled flag, API key, base URL
- [ ] 3.3 Validate HH:MM time format and 00:00–23:59 range on input
- [ ] 3.4 Create settings UI panel for schedule configuration (time list, random mode toggle, API key field)
- [ ] 3.5 Write tests for config service: invalid time format, valid HH:MM, missing API key detection

## 4. LLM Client Adapter

- [ ] 4.1 Define `llm/interface.py`: `LLMClient` protocol with `generate(prompt: str) -> str` method
- [ ] 4.2 Implement `llm/openai_client.py`: `OpenAILLMClient` using `openai` SDK, reads `base_url` and `api_key` from config at call time
- [ ] 4.3 Handle LLM timeout and API error cases — raise a typed `LLMError` exception (do not swallow silently)
- [ ] 4.4 Write tests for `OpenAILLMClient` with a mock HTTP backend: success, timeout, empty response

## 5. Fact Generation

- [ ] 5.1 Implement `content/prompts.py`: build the fact-generation prompt for a given topic (instruct LLM to return fact + optional example, under 150 words)
- [ ] 5.2 Implement `content/service.py`: `generate_fact(topic)` — picks random active topic (if none provided), calls LLM, parses response into `Fact(topic, text, example)`
- [ ] 5.3 Add deduplication check: compare generated fact against last N=10 facts for the topic; retry once if similar
- [ ] 5.4 Handle no-active-topics case: log warning and return None (caller skips popup)
- [ ] 5.5 Write tests for content service: successful generation, LLM error skips popup, no active topics, deduplication retry

## 6. Fact History

- [ ] 6.1 Implement `history/repository.py`: insert fact, query recent facts by topic, query recent facts globally, update `saved` flag, delete oldest non-saved facts
- [ ] 6.2 Enforce max-history cap (default 500): delete oldest non-saved fact before inserting when at capacity
- [ ] 6.3 Implement `history/service.py`: `save_fact(fact)`, `get_recent(topic=None, limit=10)`, `mark_saved(fact_id)`
- [ ] 6.4 Create history view UI panel (tkinter): list facts with topic, timestamp, saved indicator; filter by topic and saved status
- [ ] 6.5 Write tests for history service: cap enforcement (saved facts preserved), topic filter query, global query

## 7. Popup Display

- [ ] 7.1 Implement `popup/notification.py`: fire native OS toast notification via `plyer`; fallback to tkinter window on failure
- [ ] 7.2 Implement `popup/window.py`: tkinter window showing topic, full fact text, optional example, and three action buttons (Show Another, Save, Close)
- [ ] 7.3 Wire "Show Another" action: call `content/service.py` to generate a new fact and re-open the popup window
- [ ] 7.4 Wire "Save" action: call `history/service.py` `mark_saved(fact_id)` and close window
- [ ] 7.5 Implement `popup/tray.py`: system tray icon using `pystray` with menu items: Show Last Fact, Open Settings, Quit
- [ ] 7.6 Wire tray "Show Last Fact": query most recent fact from history and open popup window
- [ ] 7.7 Wire tray "Open Settings": open settings tkinter window
- [ ] 7.8 Write tests for popup logic: "Show Another" triggers new generation, "Save" updates history flag, empty history shows correct message

## 8. Quiz System

- [ ] 8.1 Implement `quiz/repository.py`: insert quiz attempt, query review queue items due today, mark review item resolved, update review item's next_review_date
- [ ] 8.2 Implement `quiz/prompts.py`: build quiz-generation prompt — given a source fact text, instruct LLM to produce a 4-option multiple-choice question grounded in that fact
- [ ] 8.3 Implement `quiz/service.py`: `generate_quiz()` — check review queue first, fall back to random recent fact; call LLM; return `Quiz(fact_id, question, options, correct_index)`
- [ ] 8.4 Handle insufficient history (fewer than 3 facts): return None and skip quiz
- [ ] 8.5 Implement `quiz/window.py`: tkinter window showing source fact (context), question, 4 radio-button options, Submit and Skip buttons
- [ ] 8.6 Wire correct answer: record attempt as correct, resolve review queue entry if applicable, close window
- [ ] 8.7 Wire incorrect answer: show correct answer with explanation, record attempt as incorrect, add fact to review queue (next_review_date = today + 1 day, +1 day per additional fail, max +7)
- [ ] 8.8 Wire Skip: close window without recording attempt
- [ ] 8.9 Write tests for quiz service: review queue prioritization, insufficient history returns None, incorrect answer increments review date, correct answer resolves queue item

## 9. Scheduler

- [ ] 9.1 Implement `scheduler/jobs.py`: define `fact_job()` (generate + display fact) and `quiz_job()` (generate + display quiz if enabled)
- [ ] 9.2 Implement `scheduler/service.py`: on startup, read config and register APScheduler jobs for each specific time and/or random-interval jobs
- [ ] 9.3 Implement random-interval scheduling: for each day, generate random times within the configured window (up to max-per-day) and schedule them
- [ ] 9.4 Implement quiz deferral: if a fact popup window is currently open when quiz job fires, reschedule quiz for +5 minutes
- [ ] 9.5 Re-register all jobs on startup so they survive OS restarts
- [ ] 9.6 Write tests for scheduler: specific-time job registration, random-interval count within bounds, quiz deferral when popup active

## 10. Integration & Packaging

- [ ] 10.1 Wire all modules together in `cli/main.py`: initialize DB, start scheduler, start system tray icon in main thread
- [ ] 10.2 Add startup registration: create a startup script or OS auto-start entry so the app launches on user login (Windows Task Scheduler or startup folder)
- [ ] 10.3 Create a settings window launcher accessible from tray (tabbed tkinter window with Topics, Schedule, History tabs)
- [ ] 10.4 Add a `README.md` with installation steps, how to configure API key, and how to start the app
- [ ] 10.5 Manual end-to-end test: add a topic, configure a 1-minute interval, verify popup appears with LLM-generated content, verify quiz appears after a few facts, verify incorrect answer re-appears next day
