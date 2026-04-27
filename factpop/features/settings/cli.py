from __future__ import annotations

from enum import Enum

import typer

from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Manage quiz settings.")


class QuizToggle(str, Enum):
    on = "on"
    off = "off"


def _service() -> SettingsService:
    db = get_db()
    return SettingsService(TinyDBSettingsRepository(db.table("app_config")))


@app.command("toggle")
def toggle(state: QuizToggle = typer.Argument(..., help="'on' or 'off'")) -> None:
    """Enable or disable quizzes globally."""
    enabled = state == QuizToggle.on
    _service().set_quiz_enabled(enabled)
    label = "enabled" if enabled else "disabled"
    typer.echo(f"OK: Quizzes {label}.")
