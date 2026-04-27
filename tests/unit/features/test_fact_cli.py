from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.shared.llm.errors import LLMError
from factpop.shared.llm.fake import FakeLLMClient


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def _patch_service(monkeypatch: pytest.MonkeyPatch, llm: FakeLLMClient) -> None:
    """Replace the _build_fact_service factory so CLI uses our fake LLM."""
    monkeypatch.setattr("factpop.features.facts.cli._build_llm", lambda: llm)


# --- facts generate ---

def test_cli_facts_generate_prints_fact(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Add an active topic first
    runner.invoke(app, ["topics", "add", "Java"])
    llm = FakeLLMClient(response="FACT: Java uses garbage collection.")
    _patch_service(monkeypatch, llm)

    result = runner.invoke(app, ["facts", "generate"])
    assert result.exit_code == 0
    assert "Java uses garbage collection." in result.output


def test_cli_facts_generate_with_explicit_topic(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Python"])
    llm = FakeLLMClient(response="FACT: Python is interpreted.")
    _patch_service(monkeypatch, llm)

    result = runner.invoke(app, ["facts", "generate", "--topic", "Python"])
    assert result.exit_code == 0
    assert "Python" in result.output


def test_cli_facts_generate_shows_example_when_present(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    llm = FakeLLMClient(response="FACT: Java uses generics.\nEXAMPLE: List<String> names;")
    _patch_service(monkeypatch, llm)

    result = runner.invoke(app, ["facts", "generate"])
    assert result.exit_code == 0
    assert "List<String> names;" in result.output


def test_cli_facts_generate_warns_when_no_active_topics(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    llm = FakeLLMClient(response="FACT: irrelevant.")
    _patch_service(monkeypatch, llm)

    result = runner.invoke(app, ["facts", "generate"])
    assert result.exit_code != 0
    assert "no active" in result.output.lower() or "topic" in result.output.lower()


def test_cli_facts_generate_shows_error_on_llm_failure(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    llm = FakeLLMClient(error=LLMError("connection failed"))
    _patch_service(monkeypatch, llm)

    result = runner.invoke(app, ["facts", "generate"])
    assert result.exit_code != 0


def test_cli_facts_generate_saves_to_history(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    llm = FakeLLMClient(response="FACT: Java has interfaces.")
    _patch_service(monkeypatch, llm)

    runner.invoke(app, ["facts", "generate"])
    result = runner.invoke(app, ["history", "list"])
    assert "Java" in result.output
