from __future__ import annotations

from typing import Optional

import typer

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Browse fact history.")


def _service() -> FactHistoryService:
    db = get_db()
    return FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))


@app.command("list")
def list_history(
    topic: Optional[str] = typer.Option(None, "--topic", help="Filter by topic name"),
    saved_only: bool = typer.Option(False, "--saved-only", help="Show only saved facts"),
) -> None:
    """List fact history, most recent first."""
    records = _service().get_recent(topic=topic, limit=200)

    if saved_only:
        records = [r for r in records if r.saved]

    if not records:
        typer.echo("No facts in history yet. Facts appear here after popups are shown.")
        return

    for r in records:
        status = "[saved]" if r.saved else "      "
        example_hint = "  (has example)" if r.example else ""
        typer.echo(f"{status}  [{r.topic}]  {r.shown_at[:16]}  {r.text[:60]}{example_hint}")
