"""Contract tests for LLMClient implementations.

Every implementation of LLMClient must satisfy this contract.
Real-API tests are gated behind FACTPOP_TEST_REAL_LLM=1.
"""
import os

import pytest

from factpop.features.settings.secrets import InMemorySecretStore
from factpop.shared.llm.errors import LLMAuthError
from factpop.shared.llm.fake import FakeLLMClient
from factpop.shared.llm.openai_client import OpenAICompatibleClient


def _real_secrets() -> InMemorySecretStore:
    return InMemorySecretStore({
        "FACTPOP_API_KEY": os.environ.get("FACTPOP_API_KEY", ""),
        "FACTPOP_BASE_URL": os.environ.get("FACTPOP_BASE_URL", "https://api.openai.com/v1"),
        "FACTPOP_MODEL": os.environ.get("FACTPOP_MODEL", "gpt-4o-mini"),
    })


@pytest.fixture(params=["fake", "real"])
def llm_client(request):
    if request.param == "fake":
        return FakeLLMClient(response="Java is a statically typed language.")
    # real path — skip unless explicitly enabled
    if not os.getenv("FACTPOP_TEST_REAL_LLM"):
        pytest.skip("Set FACTPOP_TEST_REAL_LLM=1 to run real LLM contract tests")
    if not os.getenv("FACTPOP_API_KEY"):
        pytest.skip("FACTPOP_API_KEY not set in environment")
    return OpenAICompatibleClient(_real_secrets())


# --- contract: every LLMClient implementation must pass these ---

def test_generate_returns_a_string(llm_client) -> None:
    result = llm_client.generate("Say hello in one word.")
    assert isinstance(result, str)


def test_generate_returns_non_empty_string(llm_client) -> None:
    result = llm_client.generate("Say hello in one word.")
    assert len(result.strip()) > 0


def test_generate_accepts_model_override(llm_client) -> None:
    result = llm_client.generate("Say hello.", model=None)
    assert isinstance(result, str)


# --- OpenAICompatibleClient-specific tests (no real API needed) ---

def test_openai_client_raises_auth_error_when_api_key_missing() -> None:
    secrets = InMemorySecretStore({"FACTPOP_API_KEY": ""})
    client = OpenAICompatibleClient(secrets)
    with pytest.raises(LLMAuthError, match="FACTPOP_API_KEY"):
        client.generate("hello")


def test_openai_client_raises_auth_error_when_api_key_not_set() -> None:
    secrets = InMemorySecretStore({})
    client = OpenAICompatibleClient(secrets)
    with pytest.raises(LLMAuthError):
        client.generate("hello")
