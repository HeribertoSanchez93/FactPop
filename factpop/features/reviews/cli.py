from __future__ import annotations

import typer

from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Manage the review queue.")


def _service() -> ReviewService:
    db = get_db()
    return ReviewService(TinyDBReviewRepository(db.table("review_queue")))


@app.command("list")
def list_reviews() -> None:
    """List all pending review queue items."""
    items = _service().get_pending()
    if not items:
        typer.echo("No pending reviews. Keep generating facts and answering quizzes!")
        return
    for item in items:
        typer.echo(f"  [{item.fact_topic}]  due: {item.next_review_date}  fails: {item.fail_count}  {item.fact_text[:50]}")
