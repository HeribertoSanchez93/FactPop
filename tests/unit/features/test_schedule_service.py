import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.schedules.errors import (
    InvalidTimeFormatError,
    TimeAlreadyExistsError,
    TimeNotFoundError,
)
from factpop.features.schedules.models import RandomModeConfig
from factpop.features.schedules.service import ScheduleService
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService


@pytest.fixture
def service() -> ScheduleService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBSettingsRepository(db.table("app_config"))
    settings = SettingsService(repo)
    return ScheduleService(settings)


# --- add_time ---

def test_add_valid_time_stores_it(service: ScheduleService) -> None:
    service.add_time("09:00")
    assert "09:00" in service.list_times()


def test_add_multiple_times(service: ScheduleService) -> None:
    service.add_time("09:00")
    service.add_time("14:00")
    assert service.list_times() == ["09:00", "14:00"]


def test_add_boundary_time_midnight(service: ScheduleService) -> None:
    service.add_time("00:00")
    assert "00:00" in service.list_times()


def test_add_boundary_time_end_of_day(service: ScheduleService) -> None:
    service.add_time("23:59")
    assert "23:59" in service.list_times()


def test_add_time_rejects_hour_over_23(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("24:00")


def test_add_time_rejects_hour_25(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("25:00")


def test_add_time_rejects_minutes_over_59(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("09:60")


def test_add_time_rejects_missing_leading_zero(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("9:00")


def test_add_time_rejects_wrong_separator(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("09-00")


def test_add_time_rejects_letters(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("ab:cd")


def test_add_time_rejects_empty_string(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("")


def test_add_duplicate_time_raises_error(service: ScheduleService) -> None:
    service.add_time("09:00")
    with pytest.raises(TimeAlreadyExistsError):
        service.add_time("09:00")


# --- remove_time ---

def test_remove_existing_time(service: ScheduleService) -> None:
    service.add_time("09:00")
    service.remove_time("09:00")
    assert "09:00" not in service.list_times()


def test_remove_nonexistent_time_raises_error(service: ScheduleService) -> None:
    with pytest.raises(TimeNotFoundError):
        service.remove_time("10:00")


def test_remove_does_not_affect_other_times(service: ScheduleService) -> None:
    service.add_time("09:00")
    service.add_time("14:00")
    service.remove_time("09:00")
    assert service.list_times() == ["14:00"]


# --- list_times ---

def test_list_times_empty_by_default(service: ScheduleService) -> None:
    assert service.list_times() == []


# --- enable_random ---

def test_enable_random_with_explicit_window(service: ScheduleService) -> None:
    service.enable_random(start="08:00", end="22:00", max_per_day=4)
    config = service.get_random_config()
    assert config.enabled is True
    assert config.start == "08:00"
    assert config.end == "22:00"
    assert config.max_per_day == 4


def test_enable_random_uses_defaults_when_no_args(service: ScheduleService) -> None:
    service.enable_random()
    config = service.get_random_config()
    assert config.enabled is True
    assert config.start == "08:00"
    assert config.end == "22:00"
    assert config.max_per_day == 3


def test_enable_random_rejects_invalid_start_time(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.enable_random(start="25:00", end="22:00", max_per_day=3)


def test_enable_random_rejects_invalid_end_time(service: ScheduleService) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.enable_random(start="08:00", end="99:00", max_per_day=3)


# --- disable_random ---

def test_disable_random_sets_enabled_to_false(service: ScheduleService) -> None:
    service.enable_random(start="08:00", end="22:00", max_per_day=3)
    service.disable_random()
    assert service.get_random_config().enabled is False


def test_disable_random_preserves_window_settings(service: ScheduleService) -> None:
    service.enable_random(start="09:00", end="21:00", max_per_day=5)
    service.disable_random()
    config = service.get_random_config()
    assert config.start == "09:00"
    assert config.end == "21:00"
    assert config.max_per_day == 5
