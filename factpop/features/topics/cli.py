from __future__ import annotations

import typer

from factpop.features.topics.errors import (
    DuplicateTopicError,
    EmptyTopicNameError,
    TopicNotFoundError,
)
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Manage learning topics.")


def _service() -> TopicService:
    db = get_db()
    return TopicService(TinyDBTopicRepository(db.table("topics")))


@app.command("add")
def add(name: str = typer.Argument(..., help="Topic name")) -> None:
    """Add a new learning topic."""
    try:
        topic = _service().create(name)
        typer.echo(f"OK: Topic '{topic.name}' added (active).")
    except EmptyTopicNameError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    except DuplicateTopicError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command("list")
def list_topics() -> None:
    """List all learning topics."""
    topics = _service().list_all()
    if not topics:
        typer.echo("No topics yet. Add one with: factpop-cli topics add <name>")
        return
    for topic in topics:
        status = "active" if topic.active else "inactive"
        typer.echo(f"  [{status}]  {topic.name}")


@app.command("activate")
def activate(name: str = typer.Argument(..., help="Topic name")) -> None:
    """Activate a topic."""
    try:
        topic = _service().activate(name)
        typer.echo(f"OK: Topic '{topic.name}' is now active.")
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command("deactivate")
def deactivate(name: str = typer.Argument(..., help="Topic name")) -> None:
    """Deactivate a topic."""
    try:
        topic, is_last = _service().deactivate(name)
        typer.echo(f"OK: Topic '{topic.name}' is now inactive.")
        if is_last:
            typer.echo(
                "Warning: no active topics remain. "
                "Popups will not fire until at least one topic is active."
            )
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command("delete")
def delete(name: str = typer.Argument(..., help="Topic name")) -> None:
    """Permanently delete a topic (fact history is preserved)."""
    try:
        _service().delete(name)
        typer.echo(f"OK: Topic '{name}' deleted.")
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
