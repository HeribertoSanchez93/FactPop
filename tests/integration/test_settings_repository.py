import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.settings.repository import TinyDBSettingsRepository


@pytest.fixture
def repo() -> TinyDBSettingsRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBSettingsRepository(db.table("app_config"))


def test_get_returns_none_when_key_not_found(repo: TinyDBSettingsRepository) -> None:
    assert repo.get("nonexistent") is None


def test_get_returns_default_when_key_not_found(repo: TinyDBSettingsRepository) -> None:
    assert repo.get("nonexistent", default="fallback") == "fallback"


def test_set_and_get_string_value(repo: TinyDBSettingsRepository) -> None:
    repo.set("api_key", "sk-abc123")
    assert repo.get("api_key") == "sk-abc123"


def test_set_and_get_bool_value(repo: TinyDBSettingsRepository) -> None:
    repo.set("quiz_enabled", False)
    assert repo.get("quiz_enabled") is False


def test_set_and_get_int_value(repo: TinyDBSettingsRepository) -> None:
    repo.set("max_per_day", 5)
    assert repo.get("max_per_day") == 5


def test_set_and_get_list_value(repo: TinyDBSettingsRepository) -> None:
    repo.set("schedule_times", ["09:00", "14:00"])
    assert repo.get("schedule_times") == ["09:00", "14:00"]


def test_set_overwrites_existing_value(repo: TinyDBSettingsRepository) -> None:
    repo.set("quiz_enabled", True)
    repo.set("quiz_enabled", False)
    assert repo.get("quiz_enabled") is False


def test_multiple_keys_are_independent(repo: TinyDBSettingsRepository) -> None:
    repo.set("key_a", "value_a")
    repo.set("key_b", "value_b")
    assert repo.get("key_a") == "value_a"
    assert repo.get("key_b") == "value_b"


def test_set_none_value_stores_none(repo: TinyDBSettingsRepository) -> None:
    repo.set("some_key", None)
    assert repo.get("some_key") is None
