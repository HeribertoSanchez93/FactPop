import pytest
from freezegun import freeze_time
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService


@pytest.fixture
def service() -> FactHistoryService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBFactHistoryRepository(db.table("fact_history"))
    return FactHistoryService(repo)


@pytest.fixture
def small_service() -> FactHistoryService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBFactHistoryRepository(db.table("fact_history"), max_size=3)
    return FactHistoryService(repo)


# --- record ---

@freeze_time("2026-04-25T10:00:00")
def test_record_returns_fact_record(service: FactHistoryService) -> None:
    r = service.record(topic="Java", text="Java uses JVM.")
    assert r.topic == "Java"
    assert r.text == "Java uses JVM."
    assert r.shown_at == "2026-04-25T10:00:00"
    assert r.saved is False


@freeze_time("2026-04-25T10:00:00")
def test_record_with_example(service: FactHistoryService) -> None:
    r = service.record(topic="Java", text="Generics.", example="List<T>")
    assert r.example == "List<T>"


def test_record_without_example_stores_none(service: FactHistoryService) -> None:
    r = service.record(topic="Java", text="A fact.")
    assert r.example is None


def test_record_persists_to_history(service: FactHistoryService) -> None:
    service.record(topic="Java", text="A fact.")
    assert service.count() == 1


def test_record_generates_unique_ids(service: FactHistoryService) -> None:
    r1 = service.record(topic="Java", text="fact 1")
    r2 = service.record(topic="Java", text="fact 2")
    assert r1.id != r2.id


# --- mark_saved ---

def test_mark_saved_updates_record(service: FactHistoryService) -> None:
    r = service.record(topic="Java", text="A fact.")
    service.mark_saved(r.id)
    recent = service.get_recent()
    assert recent[0].saved is True


# --- get_recent ---

def test_get_recent_returns_empty_when_no_history(service: FactHistoryService) -> None:
    assert service.get_recent() == []


@freeze_time("2026-04-25T10:00:00")
def test_get_recent_returns_most_recent_first(service: FactHistoryService) -> None:
    with freeze_time("2026-04-25T08:00:00"):
        service.record(topic="Java", text="oldest")
    with freeze_time("2026-04-25T10:00:00"):
        service.record(topic="Java", text="newest")
    with freeze_time("2026-04-25T09:00:00"):
        service.record(topic="Java", text="middle")

    results = service.get_recent()
    assert results[0].text == "newest"
    assert results[2].text == "oldest"


def test_get_recent_filters_by_topic(service: FactHistoryService) -> None:
    service.record(topic="Java", text="java fact")
    service.record(topic="Python", text="python fact")
    service.record(topic="Java", text="another java fact")

    results = service.get_recent(topic="Java")
    assert len(results) == 2
    assert all(r.topic == "Java" for r in results)


def test_get_recent_respects_limit(service: FactHistoryService) -> None:
    for i in range(5):
        service.record(topic="Java", text=f"fact {i}")
    results = service.get_recent(limit=3)
    assert len(results) == 3


# --- cap enforcement through service ---

def test_service_respects_cap_and_evicts_oldest_non_saved(small_service: FactHistoryService) -> None:
    with freeze_time("2026-04-25T08:00:00"):
        r1 = small_service.record(topic="Java", text="first")
    with freeze_time("2026-04-25T09:00:00"):
        small_service.record(topic="Java", text="second")
    with freeze_time("2026-04-25T10:00:00"):
        small_service.record(topic="Java", text="third")

    with freeze_time("2026-04-25T11:00:00"):
        small_service.record(topic="Java", text="fourth-triggers-eviction")

    assert small_service.count() == 3
    recent_texts = [r.text for r in small_service.get_recent()]
    assert "first" not in recent_texts


def test_service_does_not_evict_saved_facts(small_service: FactHistoryService) -> None:
    with freeze_time("2026-04-25T08:00:00"):
        r1 = small_service.record(topic="Java", text="saved-old")
        small_service.mark_saved(r1.id)
    with freeze_time("2026-04-25T09:00:00"):
        r2 = small_service.record(topic="Java", text="saved-mid")
        small_service.mark_saved(r2.id)
    with freeze_time("2026-04-25T10:00:00"):
        r3 = small_service.record(topic="Java", text="saved-new")
        small_service.mark_saved(r3.id)

    with freeze_time("2026-04-25T11:00:00"):
        small_service.record(topic="Java", text="new-triggers-overflow")

    assert small_service.count() == 4  # saved facts immune — cap exceeded temporarily
