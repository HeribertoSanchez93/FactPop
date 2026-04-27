from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


# --- topics add ---

def test_cli_topics_add_creates_topic(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "add", "Java"])
    assert result.exit_code == 0
    assert "Java" in result.output


def test_cli_topics_add_duplicate_shows_error(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "add", "Java"])
    assert result.exit_code != 0
    assert "already exists" in result.output.lower() or "duplicate" in result.output.lower()


def test_cli_topics_add_duplicate_case_insensitive(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "add", "java"])
    assert result.exit_code != 0


def test_cli_topics_add_empty_name_shows_error(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "add", ""])
    assert result.exit_code != 0


# --- topics list ---

def test_cli_topics_list_shows_existing_topics(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    runner.invoke(app, ["topics", "add", "Python"])
    result = runner.invoke(app, ["topics", "list"])
    assert result.exit_code == 0
    assert "Java" in result.output
    assert "Python" in result.output


def test_cli_topics_list_shows_active_status(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "list"])
    assert "active" in result.output.lower()


def test_cli_topics_list_empty_shows_hint(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "list"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0  # must print something (hint)


# --- topics deactivate ---

def test_cli_topics_deactivate_changes_status(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    runner.invoke(app, ["topics", "add", "Python"])
    runner.invoke(app, ["topics", "deactivate", "Java"])
    result = runner.invoke(app, ["topics", "list"])
    assert "inactive" in result.output.lower()


def test_cli_topics_deactivate_last_active_shows_warning(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "deactivate", "Java"])
    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "no active" in result.output.lower()


def test_cli_topics_deactivate_nonexistent_shows_error(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "deactivate", "NonExistent"])
    assert result.exit_code != 0


# --- topics activate ---

def test_cli_topics_activate_changes_status_to_active(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    runner.invoke(app, ["topics", "deactivate", "Java"])
    runner.invoke(app, ["topics", "activate", "Java"])
    result = runner.invoke(app, ["topics", "list"])
    assert "inactive" not in result.output.lower()


# --- topics delete ---

def test_cli_topics_delete_removes_topic(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "delete", "Java"])
    assert result.exit_code == 0
    list_result = runner.invoke(app, ["topics", "list"])
    assert "Java" not in list_result.output


def test_cli_topics_delete_nonexistent_shows_error(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "delete", "NonExistent"])
    assert result.exit_code != 0
