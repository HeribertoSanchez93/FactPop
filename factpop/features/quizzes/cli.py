from __future__ import annotations

from typing import Optional

import typer

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository
from factpop.features.quizzes.service import QuizService
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.shared.llm.client import LLMClient
from factpop.shared.llm.openai_client import OpenAICompatibleClient
from factpop.features.settings.secrets import DotenvSecretStore
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Quiz and review queue management.")


def _build_llm() -> LLMClient:
    return OpenAICompatibleClient(DotenvSecretStore())


def _build_quiz_service() -> QuizService:
    db = get_db()
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))
    attempt_repo = TinyDBQuizAttemptRepository(db.table("quiz_attempts"))
    return QuizService(
        history_service=history_svc,
        review_service=review_svc,
        llm=_build_llm(),
        attempt_repo=attempt_repo,
    )


def _build_review_service() -> ReviewService:
    db = get_db()
    return ReviewService(TinyDBReviewRepository(db.table("review_queue")))


def _build_settings_service() -> SettingsService:
    db = get_db()
    return SettingsService(TinyDBSettingsRepository(db.table("app_config")))


@app.command("toggle")
def toggle(
    state: str = typer.Argument(..., help="'on' or 'off'"),
) -> None:
    """Enable or disable quizzes globally."""
    if state not in ("on", "off"):
        typer.echo("Error: state must be 'on' or 'off'.", err=True)
        raise typer.Exit(code=1)
    enabled = state == "on"
    _build_settings_service().set_quiz_enabled(enabled)
    label = "enabled" if enabled else "disabled"
    typer.echo(f"OK: Quizzes {label}.")


@app.command("simulate")
def simulate(
    date_override: Optional[str] = typer.Option(
        None, "--date", help="Override today's date (ISO format, e.g. 2026-04-26) for testing review queue"
    ),
) -> None:
    """Generate and run a quiz interactively in the terminal."""
    svc = _build_quiz_service()
    quiz = svc.generate(as_of_date=date_override)

    if quiz is None:
        typer.echo("Not enough history to generate a quiz (need at least 3 facts). Try generating some facts first.")
        return

    # Display source fact as context
    typer.echo(f"\n[Context - {quiz.source_fact.topic}]")
    typer.echo(f"{quiz.source_fact.text}\n")

    # Display question
    typer.echo(f"QUESTION: {quiz.question}\n")
    for i, option in enumerate(quiz.options, start=1):
        typer.echo(f"  {i}. {option}")
    typer.echo("")

    # Get answer
    answer_raw = typer.prompt("Your answer (1/2/3/4) or 's' to skip").strip().lower()

    if answer_raw == "s":
        svc.skip(quiz)
        typer.echo("Quiz skipped.")
        return

    try:
        selected_index = int(answer_raw) - 1
        if selected_index not in range(4):
            raise ValueError
    except ValueError:
        typer.echo("Invalid input. Quiz skipped.")
        svc.skip(quiz)
        return

    is_correct, _ = svc.grade(quiz, selected_index=selected_index)

    if is_correct:
        typer.echo("Correct!")
    else:
        typer.echo(f"Incorrect. The correct answer was: {quiz.options[quiz.correct_index]}")
