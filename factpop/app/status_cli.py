from __future__ import annotations

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService
from factpop.features.schedules.models import RandomModeConfig
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.storage.tinydb_factory import get_db


def status_command() -> None:
    """Show a summary of topics, schedule, quiz and history state."""
    import typer

    db = get_db()
    topic_svc = TopicService(TinyDBTopicRepository(db.table("topics")))
    settings_svc = SettingsService(TinyDBSettingsRepository(db.table("app_config")))
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))

    all_topics = topic_svc.list_all()
    active_topics = topic_svc.list_active()
    schedule_times = settings_svc.get_schedule_times()
    random_cfg: RandomModeConfig = settings_svc.get_random_config()
    quiz_enabled = settings_svc.is_quiz_enabled()
    history_count = history_svc.count()
    pending_reviews = len(review_svc.get_pending())

    typer.echo("FactPop -- Current Status")
    typer.echo("=" * 36)

    typer.echo(f"\nTopics        : {len(active_topics)} active / {len(all_topics)} total")
    for t in all_topics:
        marker = "*" if t.active else " "
        typer.echo(f"  [{marker}] {t.name}")

    typer.echo(f"\nSchedule times: {len(schedule_times)} configured")
    for t in schedule_times:
        typer.echo(f"  {t}")
    if random_cfg.enabled:
        typer.echo(
            f"  Random mode : ON  ({random_cfg.start} - {random_cfg.end},"
            f" max {random_cfg.max_per_day}/day)"
        )
    else:
        typer.echo("  Random mode : OFF")

    quiz_label = "enabled" if quiz_enabled else "disabled"
    typer.echo(f"\nQuizzes       : {quiz_label}")
    typer.echo(f"Fact history  : {history_count} facts recorded")
    typer.echo(f"Review queue  : {pending_reviews} pending")
