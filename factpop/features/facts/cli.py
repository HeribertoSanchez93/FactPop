from __future__ import annotations

from typing import Optional

import typer

from factpop.features.facts.service import FactService
from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.notifications.dispatcher import NotificationDispatcher
from factpop.features.settings.secrets import DotenvSecretStore
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.llm.client import LLMClient
from factpop.shared.llm.openai_client import OpenAICompatibleClient
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Generate learning facts via LLM.")


def _build_llm() -> LLMClient:
    return OpenAICompatibleClient(DotenvSecretStore())


def _build_dispatcher() -> NotificationDispatcher:
    from factpop.features.notifications.tk_popup import TkPopupDispatcher
    return TkPopupDispatcher()


def _build_service() -> tuple[FactService, FactHistoryService]:
    db = get_db()
    topic_service = TopicService(TinyDBTopicRepository(db.table("topics")))
    history_service = FactHistoryService(
        TinyDBFactHistoryRepository(db.table("fact_history"))
    )
    fact_service = FactService(
        topic_service=topic_service,
        history_service=history_service,
        llm=_build_llm(),
    )
    return fact_service, history_service


@app.command("generate")
def generate(
    topic: Optional[str] = typer.Option(
        None, "--topic", help="Topic name (uses a random active topic if omitted)"
    ),
    show: bool = typer.Option(
        False, "--show", help="Display popup window after generating"
    ),
) -> None:
    """Generate a learning fact via LLM and save it to history."""
    svc, history_svc = _build_service()
    result = svc.generate_and_record(topic_name=topic)

    if result is None:
        typer.echo(
            "Error: Could not generate a fact. "
            "Check that active topics exist and the LLM is reachable.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"[{result.topic}] {result.text}")
    if result.example:
        typer.echo(f"\nExample:\n{result.example}")

    if show:
        dispatcher = _build_dispatcher()
        record_id = result.id

        def on_save() -> None:
            history_svc.mark_saved(record_id)

        def on_show_another() -> None:
            new_result = svc.generate_and_record()
            if new_result:
                dispatcher.show_fact(
                    new_result,
                    on_save=lambda: history_svc.mark_saved(new_result.id),
                    on_show_another=on_show_another,
                )

        dispatcher.show_fact(result, on_save=on_save, on_show_another=on_show_another)
