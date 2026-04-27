from __future__ import annotations

import typer

from factpop.app.auto_start_cli import app as autostart_cli_app
from factpop.app.status_cli import status_command
from factpop.features.facts import cli as facts_cli
from factpop.features.history import cli as history_cli
from factpop.features.quizzes import cli as quizzes_cli
from factpop.features.reviews import cli as reviews_cli
from factpop.features.schedules import cli as schedules_cli
from factpop.features.topics import cli as topics_cli
from factpop.shared.llm import cli as llm_cli

app = typer.Typer(name="factpop-cli", help="FactPop admin CLI")
app.add_typer(topics_cli.app, name="topics")
app.add_typer(schedules_cli.app, name="schedules")
app.add_typer(quizzes_cli.app, name="quiz")
app.add_typer(llm_cli.app, name="llm")
app.add_typer(history_cli.app, name="history")
app.add_typer(facts_cli.app, name="facts")
app.add_typer(reviews_cli.app, name="reviews")
app.add_typer(autostart_cli_app, name="autostart")
app.command("status")(status_command)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
