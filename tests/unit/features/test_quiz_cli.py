from pathlib import Path

import pytest
from freezegun import freeze_time
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.shared.llm.fake import FakeLLMClient

_VALID_QUIZ_RESPONSE = (
    "QUESTION: What does Java use for memory management?\n"
    "A: Manual deallocation\n"
    "B: Garbage collection\n"
    "C: Reference counting\n"
    "D: Stack-only allocation\n"
    "CORRECT: B"
)


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def _add_facts(count: int = 3) -> None:
    db = db_module.get_db()
    svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    for i in range(count):
        svc.record(topic="Java", text=f"Java fact {i}. Some content here.")


def _patch_llm(monkeypatch: pytest.MonkeyPatch, response: str = _VALID_QUIZ_RESPONSE) -> FakeLLMClient:
    llm = FakeLLMClient(response=response)
    monkeypatch.setattr("factpop.features.quizzes.cli._build_llm", lambda: llm)
    return llm


# --- quiz simulate: insufficient history ---

def test_quiz_simulate_with_no_history_shows_skip_message(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_llm(monkeypatch)
    result = runner.invoke(app, ["quiz", "simulate"])
    assert result.exit_code == 0
    assert "skip" in result.output.lower() or "not enough" in result.output.lower() or "insufficient" in result.output.lower()


# --- quiz simulate: normal flow ---

def test_quiz_simulate_shows_question_and_options(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    result = runner.invoke(app, ["quiz", "simulate"], input="s\n")
    assert result.exit_code == 0
    assert "QUESTION" in result.output or "?" in result.output


def test_quiz_simulate_shows_source_fact_context(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    result = runner.invoke(app, ["quiz", "simulate"], input="s\n")
    assert "Java fact" in result.output


def test_quiz_simulate_correct_answer_shows_correct(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    # B = index 1 = answer "2"
    result = runner.invoke(app, ["quiz", "simulate"], input="2\n")
    assert "correct" in result.output.lower()


def test_quiz_simulate_wrong_answer_shows_incorrect_and_correct_answer(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    # A = index 0 = answer "1" (wrong, correct is B=2)
    result = runner.invoke(app, ["quiz", "simulate"], input="1\n")
    assert "incorrect" in result.output.lower() or "wrong" in result.output.lower()
    assert "Garbage collection" in result.output


def test_quiz_simulate_skip_records_no_attempt(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    runner.invoke(app, ["quiz", "simulate"], input="s\n")
    # No attempts in history — verify indirectly by checking reviews list is empty
    result = runner.invoke(app, ["reviews", "list"])
    assert "no pending" in result.output.lower() or result.output.strip() == "" or "0" in result.output


def test_quiz_simulate_wrong_answer_adds_to_review_queue(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    runner.invoke(app, ["quiz", "simulate"], input="1\n")  # wrong answer
    result = runner.invoke(app, ["reviews", "list"])
    assert "Java" in result.output


# --- reviews list ---

def test_reviews_list_empty_shows_hint(
    runner: CliRunner, tmp_path: Path
) -> None:
    result = runner.invoke(app, ["reviews", "list"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0
