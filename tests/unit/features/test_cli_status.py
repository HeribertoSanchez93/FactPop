"""Tests for factpop-cli status command."""
from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def _seed_topics(runner: CliRunner, names: list[str]) -> None:
    for name in names:
        runner.invoke(app, ["topics", "add", name])


# ── status command structure ─────────────────────────────────────────────────

def test_status_exits_successfully(runner: CliRunner) -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0


def test_status_shows_topics_section(runner: CliRunner) -> None:
    _seed_topics(runner, ["Java", "Python"])
    result = runner.invoke(app, ["status"])
    assert "topic" in result.output.lower()


def test_status_shows_correct_active_topic_count(runner: CliRunner) -> None:
    _seed_topics(runner, ["Java", "Python", "Kafka"])
    result = runner.invoke(app, ["status"])
    assert "3" in result.output


def test_status_shows_schedule_section(runner: CliRunner) -> None:
    runner.invoke(app, ["schedules", "add", "09:00"])
    result = runner.invoke(app, ["status"])
    assert "schedule" in result.output.lower() or "09:00" in result.output


def test_status_shows_quiz_enabled_state(runner: CliRunner) -> None:
    runner.invoke(app, ["quiz", "toggle", "off"])
    result = runner.invoke(app, ["status"])
    assert "quiz" in result.output.lower()
    assert "disabled" in result.output.lower() or "off" in result.output.lower()


def test_status_shows_history_count(runner: CliRunner) -> None:
    db = db_module.get_db()
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    history_svc.record("Java", "Java fact.")
    history_svc.record("Java", "Another fact.")
    result = runner.invoke(app, ["status"])
    assert "history" in result.output.lower() or "fact" in result.output.lower()
    assert "2" in result.output


def test_status_shows_review_queue_count(runner: CliRunner, tmp_path: Path) -> None:
    db = db_module.get_db()
    from factpop.features.history.models import FactRecord
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))
    record = FactRecord(id="f1", topic="Java", text="A fact.", shown_at="2026-04-26T10:00:00")
    review_svc.enqueue(record)
    result = runner.invoke(app, ["status"])
    assert "review" in result.output.lower() or "pending" in result.output.lower()


def test_status_no_topics_shows_zero_or_hint(runner: CliRunner) -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "0" in result.output or "no topic" in result.output.lower()
