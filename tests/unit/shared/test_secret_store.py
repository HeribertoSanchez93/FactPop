import os
from unittest.mock import patch

import pytest

from factpop.features.settings.secrets import DotenvSecretStore, InMemorySecretStore


# --- InMemorySecretStore ---

def test_in_memory_get_returns_value() -> None:
    store = InMemorySecretStore({"FACTPOP_API_KEY": "sk-test"})
    assert store.get("FACTPOP_API_KEY") == "sk-test"


def test_in_memory_get_returns_none_for_missing_key() -> None:
    store = InMemorySecretStore({})
    assert store.get("MISSING_KEY") is None


def test_in_memory_get_returns_default_for_missing_key() -> None:
    store = InMemorySecretStore({})
    assert store.get("MISSING_KEY", default="fallback") == "fallback"


def test_in_memory_get_does_not_return_default_when_key_exists() -> None:
    store = InMemorySecretStore({"KEY": "real_value"})
    assert store.get("KEY", default="fallback") == "real_value"


def test_in_memory_stores_multiple_keys() -> None:
    store = InMemorySecretStore({
        "FACTPOP_API_KEY": "sk-abc",
        "FACTPOP_BASE_URL": "https://api.example.com/v1",
    })
    assert store.get("FACTPOP_API_KEY") == "sk-abc"
    assert store.get("FACTPOP_BASE_URL") == "https://api.example.com/v1"


# --- DotenvSecretStore ---

def test_dotenv_store_reads_from_environment() -> None:
    with patch.dict(os.environ, {"FACTPOP_API_KEY": "sk-from-env"}):
        store = DotenvSecretStore()
        assert store.get("FACTPOP_API_KEY") == "sk-from-env"


def test_dotenv_store_returns_none_for_missing_key() -> None:
    with patch.dict(os.environ, {}, clear=False):
        store = DotenvSecretStore()
        result = store.get("FACTPOP_NONEXISTENT_KEY_XYZ")
        assert result is None


def test_dotenv_store_returns_default_for_missing_key() -> None:
    with patch.dict(os.environ, {}, clear=False):
        store = DotenvSecretStore()
        result = store.get("FACTPOP_NONEXISTENT_KEY_XYZ", default="default_val")
        assert result == "default_val"
