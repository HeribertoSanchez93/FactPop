"""Tests for the --show flag in 'facts generate'.

The dispatcher (tkinter, plyer) is replaced by NullDispatcher via monkeypatch,
so these tests run without a display server.
"""
from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.features.notifications.null import NullDispatcher
from factpop.shared.llm.fake import FakeLLMClient


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def _patch_llm(monkeypatch: pytest.MonkeyPatch, response: str) -> FakeLLMClient:
    llm = FakeLLMClient(response=response)
    monkeypatch.setattr("factpop.features.facts.cli._build_llm", lambda: llm)
    return llm


def _patch_dispatcher(monkeypatch: pytest.MonkeyPatch) -> NullDispatcher:
    disp = NullDispatcher()
    monkeypatch.setattr("factpop.features.facts.cli._build_dispatcher", lambda: disp)
    return disp


# --- --show flag triggers dispatcher ---

def test_show_flag_calls_dispatcher_once(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    _patch_llm(monkeypatch, "FACT: Java uses the JVM.")
    disp = _patch_dispatcher(monkeypatch)

    result = runner.invoke(app, ["facts", "generate", "--show"])
    assert result.exit_code == 0
    assert disp.shown_count == 1


def test_show_flag_passes_correct_record_to_dispatcher(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Python"])
    _patch_llm(monkeypatch, "FACT: Python uses indentation.")
    disp = _patch_dispatcher(monkeypatch)

    runner.invoke(app, ["facts", "generate", "--show", "--topic", "Python"])
    assert disp.last_record is not None
    assert disp.last_record.topic == "Python"
    assert disp.last_record.text == "Python uses indentation."


def test_without_show_flag_dispatcher_is_not_called(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    _patch_llm(monkeypatch, "FACT: Java uses the JVM.")
    disp = _patch_dispatcher(monkeypatch)

    runner.invoke(app, ["facts", "generate"])
    assert disp.shown_count == 0


# --- on_save callback marks fact as saved ---

def test_on_save_callback_marks_fact_saved(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    _patch_llm(monkeypatch, "FACT: Java uses the JVM.")
    disp = _patch_dispatcher(monkeypatch)

    runner.invoke(app, ["facts", "generate", "--show"])
    disp.trigger_save()

    history_result = runner.invoke(app, ["history", "list", "--saved-only"])
    assert "Java" in history_result.output


def test_on_close_does_not_mark_fact_saved(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    _patch_llm(monkeypatch, "FACT: Java uses the JVM.")
    disp = _patch_dispatcher(monkeypatch)

    runner.invoke(app, ["facts", "generate", "--show"])
    disp.trigger_close()

    history_result = runner.invoke(app, ["history", "list", "--saved-only"])
    assert "Java" not in history_result.output


# --- no active topics ---

def test_show_flag_with_no_active_topics_exits_with_error(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_llm(monkeypatch, "FACT: irrelevant.")
    disp = _patch_dispatcher(monkeypatch)

    result = runner.invoke(app, ["facts", "generate", "--show"])
    assert result.exit_code != 0
    assert disp.shown_count == 0
