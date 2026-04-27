from pathlib import Path

import pytest
from freezegun import freeze_time
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def _add_fact(tmp_path: Path, topic: str, text: str, saved: bool = False) -> None:
    """Helper: directly insert a fact into the test DB."""
    db = db_module.get_db()
    repo = TinyDBFactHistoryRepository(db.table("fact_history"))
    svc = FactHistoryService(repo)
    r = svc.record(topic=topic, text=text)
    if saved:
        svc.mark_saved(r.id)


# --- history list ---

def test_cli_history_list_shows_all_facts(runner: CliRunner, tmp_path: Path) -> None:
    _add_fact(tmp_path, "Java", "Java uses JVM.")
    _add_fact(tmp_path, "Python", "Python is interpreted.")
    result = runner.invoke(app, ["history", "list"])
    assert result.exit_code == 0
    assert "Java" in result.output
    assert "Python" in result.output


def test_cli_history_list_empty_shows_hint(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(app, ["history", "list"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_cli_history_list_filter_by_topic(runner: CliRunner, tmp_path: Path) -> None:
    _add_fact(tmp_path, "Java", "Java is compiled.")
    _add_fact(tmp_path, "Python", "Python uses indentation.")
    result = runner.invoke(app, ["history", "list", "--topic", "Java"])
    assert result.exit_code == 0
    assert "Java" in result.output
    assert "Python" not in result.output


def test_cli_history_list_filter_saved_only(runner: CliRunner, tmp_path: Path) -> None:
    _add_fact(tmp_path, "Java", "unsaved fact", saved=False)
    _add_fact(tmp_path, "Java", "saved fact", saved=True)
    result = runner.invoke(app, ["history", "list", "--saved-only"])
    assert result.exit_code == 0
    assert "saved fact" in result.output
    assert "unsaved fact" not in result.output


def test_cli_history_list_shows_saved_status(runner: CliRunner, tmp_path: Path) -> None:
    _add_fact(tmp_path, "Java", "some fact", saved=True)
    result = runner.invoke(app, ["history", "list"])
    assert "saved" in result.output.lower()
