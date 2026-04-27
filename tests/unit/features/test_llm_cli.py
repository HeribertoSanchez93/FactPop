from pathlib import Path

import pytest
from typer.testing import CliRunner

import factpop.shared.storage.tinydb_factory as db_module
from factpop.app.cli import app
from factpop.features.settings.secrets import InMemorySecretStore
from factpop.shared.llm.fake import FakeLLMClient


@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()


def test_cli_llm_ping_succeeds_with_valid_credentials(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeLLMClient(response="pong")
    monkeypatch.setattr(
        "factpop.shared.llm.cli._build_client",
        lambda: fake,
    )
    result = runner.invoke(app, ["llm", "ping"])
    assert result.exit_code == 0
    assert "pong" in result.output


def test_cli_llm_ping_shows_error_when_api_key_missing(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    from factpop.shared.llm.errors import LLMAuthError

    def _raise(_):
        raise LLMAuthError("FACTPOP_API_KEY is not set.")

    monkeypatch.setattr("factpop.shared.llm.cli._build_client", lambda: _make_error_client())
    result = runner.invoke(app, ["llm", "ping"])
    assert result.exit_code != 0
    assert "api_key" in result.output.lower() or "key" in result.output.lower()


def _make_error_client():
    from factpop.shared.llm.errors import LLMAuthError
    return FakeLLMClient(error=LLMAuthError("FACTPOP_API_KEY is not set. Check your .env file."))
