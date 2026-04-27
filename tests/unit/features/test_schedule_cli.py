from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


# --- schedules add ---

def test_cli_schedules_add_valid_time(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "add", "09:00"])
    assert result.exit_code == 0
    assert "09:00" in result.output


def test_cli_schedules_add_invalid_hour(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "add", "25:00"])
    assert result.exit_code != 0
    assert "invalid" in result.output.lower() or "format" in result.output.lower()


def test_cli_schedules_add_invalid_minutes(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "add", "09:61"])
    assert result.exit_code != 0


def test_cli_schedules_add_missing_leading_zero(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "add", "9:00"])
    assert result.exit_code != 0


def test_cli_schedules_add_duplicate_shows_error(runner: CliRunner) -> None:
    runner.invoke(app, ["schedules", "add", "09:00"])
    result = runner.invoke(app, ["schedules", "add", "09:00"])
    assert result.exit_code != 0
    assert "already" in result.output.lower()


# --- schedules remove ---

def test_cli_schedules_remove_existing_time(runner: CliRunner) -> None:
    runner.invoke(app, ["schedules", "add", "09:00"])
    result = runner.invoke(app, ["schedules", "remove", "09:00"])
    assert result.exit_code == 0
    assert "09:00" in result.output


def test_cli_schedules_remove_nonexistent_shows_error(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "remove", "10:00"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


# --- schedules list ---

def test_cli_schedules_list_shows_configured_times(runner: CliRunner) -> None:
    runner.invoke(app, ["schedules", "add", "09:00"])
    runner.invoke(app, ["schedules", "add", "14:00"])
    result = runner.invoke(app, ["schedules", "list"])
    assert result.exit_code == 0
    assert "09:00" in result.output
    assert "14:00" in result.output


def test_cli_schedules_list_shows_hint_when_empty(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "list"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


# --- schedules random enable ---

def test_cli_schedules_random_enable_with_all_options(runner: CliRunner) -> None:
    result = runner.invoke(
        app,
        ["schedules", "random", "enable", "--start", "08:00", "--end", "22:00", "--max", "4"],
    )
    assert result.exit_code == 0
    assert "enabled" in result.output.lower()


def test_cli_schedules_random_enable_uses_defaults(runner: CliRunner) -> None:
    result = runner.invoke(app, ["schedules", "random", "enable"])
    assert result.exit_code == 0
    assert "08:00" in result.output
    assert "22:00" in result.output


def test_cli_schedules_random_enable_invalid_start(runner: CliRunner) -> None:
    result = runner.invoke(
        app,
        ["schedules", "random", "enable", "--start", "99:00", "--end", "22:00"],
    )
    assert result.exit_code != 0


# --- schedules random disable ---

def test_cli_schedules_random_disable(runner: CliRunner) -> None:
    runner.invoke(app, ["schedules", "random", "enable"])
    result = runner.invoke(app, ["schedules", "random", "disable"])
    assert result.exit_code == 0
    assert "disabled" in result.output.lower()


# --- quiz toggle ---

def test_cli_quiz_toggle_off(runner: CliRunner) -> None:
    result = runner.invoke(app, ["quiz", "toggle", "off"])
    assert result.exit_code == 0
    assert "disabled" in result.output.lower()


def test_cli_quiz_toggle_on(runner: CliRunner) -> None:
    runner.invoke(app, ["quiz", "toggle", "off"])
    result = runner.invoke(app, ["quiz", "toggle", "on"])
    assert result.exit_code == 0
    assert "enabled" in result.output.lower()


def test_cli_quiz_toggle_invalid_value(runner: CliRunner) -> None:
    result = runner.invoke(app, ["quiz", "toggle", "maybe"])
    assert result.exit_code != 0
