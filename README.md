# FactPop

A local background app that shows LLM-generated learning popups while you work.

FactPop runs silently in the system tray and periodically surfaces bite-sized facts about topics you define. Optional quizzes reinforce retention by testing you on facts you've already seen.

> **Status: MVP in progress**
> This application works and can be used, but it is still under active development. As an MVP, it may contain bugs or unexpected behavior that will be addressed in future iterations. If you encounter an issue, it is part of the process.

---

## About this project

**Author: Heriberto Daniel Sanchez Peña**

This is my first project built using **Spec-Driven Development (SDD)** and **Test-Driven Development (TDD)**, and I want to be transparent about how it was made.

I am a **Java developer**. Python is not my primary language — I had never written a Python project before this one. Despite that, I was able to build a fully functional, well-structured, tested application by applying two methodologies I wanted to learn and prove I could direct:

### How it was built

The project was created using a deliberate multi-role AI-assisted workflow, with each role defined by a carefully crafted initial prompt:

**Role 1 — Architect**
The architect role was responsible for transforming the product idea into a clear product definition, a modular architecture, and a full set of capability specifications. It produced the design documents, the MVP scope, and the spec files that live under `openspec/`.

**Role 2 — Tech Lead**
The tech lead role took those architect artifacts and converted them into a concrete technical design: stack selection (Python 3.13, TinyDB, `schedule`, tkinter), module structure, SOLID principles, patterns (Adapter, Repository, DI), and a stage-by-stage implementation roadmap — all before writing a single line of code.

Both roles were invoked using structured prompts that gave them specific responsibilities and constraints, preventing them from drifting into unbounded code generation.

### My role: directing, reviewing, and approving

I did not give the AI free rein. My role throughout was to:

- Define what I wanted to build and the constraints (local app, no cloud, no microservices, no overengineering)
- Review the output of each stage before approving the next one
- Reject or correct work that did not meet the spec
- Make architectural decisions when alternatives were presented
- Validate that each gate of acceptance actually passed

The implementation was done **stage by stage** — 10 stages total — and I approved each one before the next began. This is how a senior engineer would manage a team: not by writing every line themselves, but by ensuring quality at each checkpoint.

### The `explicaciones/` folder

Since I am not a Python developer, a dedicated folder called **`explicaciones/`** was created exclusively for me. For every file written in every stage, there is a Markdown document explaining what each line of code does, why it was written that way, and what would break if it were removed. This is not documentation for end users — it is my learning record, proof that I understood what was being built, not just that it was built.

### Why this matters

This project exists to demonstrate something specific: **I am capable of using modern AI-assisted development methodologies to deliver real software, even in a language I do not know.**

The goal is not the Python app itself. The goal is to show that I can:
- Apply SDD to go from vague idea to structured specs
- Apply TDD to go from specs to verified, tested code
- Direct AI tools as a technical lead without losing control of quality
- Review and validate output at every stage
- Build systems that are modular, testable, and maintainable

This is not my last project using SDD and TDD. I will continue building things, improving my methodology, and creating proof of what I can do.

**If you want to use FactPop, it is free.** Take it, fork it, improve it.

---

## Requirements

- **Python 3.13** — download from [python.org](https://python.org)
- **OpenAI-compatible API key** — works with OpenAI, Venice AI, Ollama, or any compatible provider
- **Windows 10/11** (primary target; macOS/Linux may work with minor adjustments)

## Installation

```powershell
# 1. Clone or download the project
cd path\to\FactPop

# 2. Run the setup script (creates .venv, installs deps, copies .env.example -> .env)
.\scripts\bootstrap_dev.ps1

# 3. Edit .env with your API credentials
notepad .env
```

Your `.env` should contain:
```
FACTPOP_API_KEY=your-api-key-here
FACTPOP_BASE_URL=https://api.openai.com/v1
FACTPOP_MODEL=gpt-4o-mini
```

## Starting FactPop

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Start the daemon (shows system tray icon)
python -m factpop
```

Right-click the tray icon to access: **Show Last Fact**, **Open Settings**, **Quit**.

## Configure topics and schedule

Use the Settings window (tray icon -> Open Settings), or the CLI:

```powershell
# Add learning topics
factpop-cli topics add Java
factpop-cli topics add "AWS IAM - role groups"
factpop-cli topics add "Spring Boot"

# Configure popup times
factpop-cli schedules add 09:00
factpop-cli schedules add 14:00

# Or use random mode
factpop-cli schedules random enable --start 08:00 --end 22:00 --max 3

# Enable quizzes
factpop-cli quiz toggle on

# Check current configuration
factpop-cli status
```

## Test the LLM connection

```powershell
factpop-cli llm ping
```

## Generate a fact manually

```powershell
# Generate and display a popup
factpop-cli facts generate --show

# Generate for a specific topic
factpop-cli facts generate --topic "Java" --show
```

## View history and review queue

```powershell
factpop-cli history list
factpop-cli history list --topic Java
factpop-cli history list --saved-only
factpop-cli reviews list
```

## Auto-start on Windows login

```powershell
# Install startup script (runs silently on login)
factpop-cli autostart install

# Remove auto-start
factpop-cli autostart remove

# Check status
factpop-cli autostart status
```

## Run tests

```powershell
.\scripts\run_tests.ps1

# Run only unit tests
.\scripts\run_tests.ps1 tests/unit

# Run real LLM contract tests (requires API key in .env)
$env:FACTPOP_TEST_REAL_LLM=1; .\.venv\Scripts\pytest tests/contract -v
```

## Project layout

```
factpop/
  app/           Entry points, lifecycle, bootstrap, tray icon
  features/
    topics/      Topic management (CRUD + active/inactive)
    schedules/   Schedule configuration (times + random mode)
    facts/       Fact generation via LLM
    notifications/ Popup dispatcher + tkinter window
    history/     Fact history persistence
    quizzes/     Quiz generation + grading
    reviews/     Review queue (spaced repetition scaffold)
    settings/    App config, secrets, settings window
  shared/
    llm/         LLM client adapter (OpenAI-compatible)
    scheduler/   Background job scheduler
    storage/     TinyDB factory + helpers
    errors.py    Exception hierarchy

explicaciones/   Per-stage line-by-line explanations (learning record)
openspec/        Architecture specs and design documents
.env             Your API credentials (never committed)
.env.example     Template -- copy to .env and fill in your key
```

## Data storage

All data is stored locally at `%APPDATA%\FactPop\FactPop\factpop.json`.
Logs are at `%LOCALAPPDATA%\FactPop\FactPop\Logs\factpop.log`.

To reset all data: delete the `%APPDATA%\FactPop\` folder and restart.
