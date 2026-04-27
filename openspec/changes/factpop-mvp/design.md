## Context

FactPop is a new standalone local application with no prior codebase. It runs as a background process on the user's desktop OS (Windows primary target), periodically surfacing native OS popup notifications containing LLM-generated learning facts. The user has an OpenAI-compatible API key and wants zero cloud infrastructure — all state lives on disk.

Key constraints derived from requirements:
- No server, no accounts, no microservices
- LLM is external (OpenAI-compatible API) but the rest is local
- Must survive OS restarts (scheduler re-registers on startup)
- Quiz content must be grounded in previously shown facts — no hallucinated quiz questions

## Goals / Non-Goals

**Goals:**
- Define module boundaries so each capability (topics, scheduler, LLM client, popup, history, quiz) can be built and tested independently
- Choose a simple, proven local tech stack that avoids distributed-system complexity
- Design the LLM client as a replaceable adapter behind a stable interface
- Design the quiz system to be extendable toward spaced repetition without requiring it in MVP
- Ensure all state persists in a single local SQLite database file

**Non-Goals:**
- Web dashboard, mobile app, or any remote UI
- Cloud sync, user accounts, or social features
- Advanced spaced repetition algorithm (SM-2 or similar) in MVP
- Multi-user or multi-device support
- Real-time LLM streaming in popups

## Decisions

### Decision 1: Runtime — Python with SQLite

**Choice:** Python 3.11+ application using SQLite (via `sqlite3` stdlib or SQLAlchemy Core) for all persistence.

**Rationale:** Python has first-class support for the entire required stack: `openai` SDK (OpenAI-compatible), `schedule`/`APScheduler` for background scheduling, `plyer` or `win10toast` for OS notifications, `tkinter` or `customtkinter` for popup windows, and SQLite for local storage. A single Python process with no external runtime dependencies meets the "simple local app" constraint.

**Alternatives considered:**
- Electron/Node.js: heavier runtime, more complex packaging, JS async complexity adds no value here
- Rust: excellent for background apps but slower development cycle for a personal tool
- Go: good binary packaging but fewer LLM/notification ecosystem libs

### Decision 2: Module Structure (6 modules, 1 shared DB layer)

```
factpop/
  db/           # SQLite schema, migrations, connection management
  topics/       # Topic CRUD + active/inactive state
  config/       # Schedule config (times list, random mode toggle, quiz toggle)
  llm/          # LLM adapter interface + OpenAI implementation
  content/      # Fact generation logic (orchestrates topics + llm + history)
  popup/        # Native OS notification + optional tkinter popup window
  history/      # Fact storage and retrieval
  quiz/         # Quiz generation from history, answer recording, re-queue logic
  scheduler/    # Background job runner (APScheduler); wires content + popup + quiz
  cli/          # Entry point: start daemon, open settings UI
```

**Rationale:** Each module owns one concern. The scheduler is a wiring layer only — it never generates content or manages DB records directly. The LLM client is injected into `content/` as an adapter, making it swappable.

### Decision 3: LLM Client as Replaceable Adapter

**Choice:** Define a `LLMClient` protocol/interface with a single `generate(prompt: str) -> str` method. The `OpenAILLMClient` implements it using the `openai` Python SDK with `base_url` configurable so any OpenAI-compatible endpoint works.

**Rationale:** Isolates LLM provider details from business logic. Future swap to Ollama, Anthropic, or a local model requires only a new adapter class, not changes to content generation logic.

### Decision 4: Popup Strategy — OS Notification + Optional Detail Window

**Choice:** Use OS-native toast notifications (via `plyer`) for the primary popup. When the user clicks the notification or chooses "show more," a small `tkinter` window opens with full fact content and action buttons (Show Another, Save, Close).

**Rationale:** Toast notifications are non-intrusive and work system-wide. The tkinter window is only shown on demand, keeping the default experience lightweight. Avoids a full GUI framework dependency.

### Decision 5: Quiz Storage and Re-queue

**Choice:** Quiz results stored in a `quiz_attempts` table. Incorrect answers stored in `review_queue` table with a `next_review_date` field (initially set to same day or +1 day). The scheduler checks `review_queue` before generating a new quiz and prioritizes pending reviews.

**Rationale:** This simple date-based queue is sufficient for MVP and can be replaced with SM-2 scoring in a future iteration by adding a `difficulty_factor` column — no structural redesign needed.

### Decision 6: Configuration Storage

**Choice:** All user configuration (topic list, schedule times, random mode flag, quiz enabled flag, API key, API base URL) stored in a `config` table in SQLite as key-value pairs, plus a dedicated `topics` table.

**Rationale:** Keeps everything in one file. No separate JSON/TOML config files to keep in sync. API key stored locally (not in source control) — acceptable for a personal tool.

## Risks / Trade-offs

- **OS notification reliability on Windows** → Mitigation: Fall back to tkinter popup window if `plyer` toast fails; test on Windows 10/11 specifically
- **LLM API latency blocks scheduler thread** → Mitigation: Run LLM calls in a separate thread or async task; popup is triggered only after generation completes, with a timeout fallback
- **Fact history grows unbounded** → Mitigation: Add a configurable max-history cap (default: last 500 facts) to keep quiz source manageable and DB size small
- **Quiz questions may repeat before all facts are covered** → Mitigation: Track which facts have been quizzed; prefer unquizzed facts in quiz selection; acceptable limitation for MVP
- **APScheduler state lost on crash** → Mitigation: APScheduler with `SQLAlchemyJobStore` persists jobs to SQLite; alternatively, use in-memory scheduler with startup re-registration from config (simpler for MVP)
- **API key stored in plaintext SQLite** → Trade-off accepted: this is a personal local tool; user is responsible for their machine security
