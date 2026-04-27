import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.schedules.models import RandomModeConfig
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService


@pytest.fixture
def service() -> SettingsService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBSettingsRepository(db.table("app_config"))
    return SettingsService(repo)


# --- schedule_times ---

def test_get_schedule_times_returns_empty_list_by_default(service: SettingsService) -> None:
    assert service.get_schedule_times() == []


def test_set_and_get_schedule_times(service: SettingsService) -> None:
    service.set_schedule_times(["09:00", "14:00"])
    assert service.get_schedule_times() == ["09:00", "14:00"]


def test_set_schedule_times_overwrites_previous(service: SettingsService) -> None:
    service.set_schedule_times(["09:00"])
    service.set_schedule_times(["10:00", "16:00"])
    assert service.get_schedule_times() == ["10:00", "16:00"]


# --- quiz_enabled ---

def test_quiz_is_enabled_by_default(service: SettingsService) -> None:
    assert service.is_quiz_enabled() is True


def test_set_quiz_enabled_false(service: SettingsService) -> None:
    service.set_quiz_enabled(False)
    assert service.is_quiz_enabled() is False


def test_set_quiz_enabled_true_after_false(service: SettingsService) -> None:
    service.set_quiz_enabled(False)
    service.set_quiz_enabled(True)
    assert service.is_quiz_enabled() is True


# --- random_config ---

def test_get_random_config_returns_defaults(service: SettingsService) -> None:
    config = service.get_random_config()
    assert config.enabled is False
    assert config.start == "08:00"
    assert config.end == "22:00"
    assert config.max_per_day == 3


def test_set_random_config_persists_all_fields(service: SettingsService) -> None:
    new_config = RandomModeConfig(enabled=True, start="09:00", end="21:00", max_per_day=5)
    service.set_random_config(new_config)
    saved = service.get_random_config()
    assert saved.enabled is True
    assert saved.start == "09:00"
    assert saved.end == "21:00"
    assert saved.max_per_day == 5


def test_set_random_config_disable_only_changes_enabled(service: SettingsService) -> None:
    service.set_random_config(RandomModeConfig(enabled=True, start="10:00", end="20:00", max_per_day=4))
    service.set_random_config(RandomModeConfig(enabled=False, start="10:00", end="20:00", max_per_day=4))
    config = service.get_random_config()
    assert config.enabled is False
    assert config.start == "10:00"
