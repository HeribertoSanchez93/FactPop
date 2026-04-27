import time

import pytest
from freezegun import freeze_time
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.history.models import FactRecord
from factpop.features.history.repository import TinyDBFactHistoryRepository


def _make_record(topic: str = "Java", text: str = "fact", shown_at: str = "2026-04-25T10:00:00") -> FactRecord:
    import uuid
    return FactRecord(id=str(uuid.uuid4()), topic=topic, text=text, shown_at=shown_at)


@pytest.fixture
def repo() -> TinyDBFactHistoryRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBFactHistoryRepository(db.table("fact_history"))


@pytest.fixture
def small_repo() -> TinyDBFactHistoryRepository:
    """Repository with cap=3 for testing eviction without 500 records."""
    db = TinyDB(storage=MemoryStorage)
    return TinyDBFactHistoryRepository(db.table("fact_history"), max_size=3)


# --- insert ---

def test_insert_stores_record(repo: TinyDBFactHistoryRepository) -> None:
    r = _make_record()
    repo.insert(r)
    assert repo.count() == 1


def test_insert_preserves_all_fields(repo: TinyDBFactHistoryRepository) -> None:
    r = FactRecord(
        id="abc", topic="Java", text="Generics exist.",
        shown_at="2026-04-25T10:00:00", example="List<T>", saved=False
    )
    repo.insert(r)
    found = repo.find_by_id("abc")
    assert found is not None
    assert found.topic == "Java"
    assert found.text == "Generics exist."
    assert found.example == "List<T>"
    assert found.saved is False


def test_insert_stores_record_with_none_example(repo: TinyDBFactHistoryRepository) -> None:
    r = _make_record()
    repo.insert(r)
    found = repo.find_by_id(r.id)
    assert found is not None
    assert found.example is None


# --- cap enforcement ---

def test_insert_evicts_oldest_non_saved_when_at_cap(small_repo: TinyDBFactHistoryRepository) -> None:
    r1 = _make_record(text="oldest", shown_at="2026-04-25T08:00:00")
    r2 = _make_record(text="middle", shown_at="2026-04-25T09:00:00")
    r3 = _make_record(text="newest-before-cap", shown_at="2026-04-25T10:00:00")
    small_repo.insert(r1)
    small_repo.insert(r2)
    small_repo.insert(r3)

    r4 = _make_record(text="triggers-eviction", shown_at="2026-04-25T11:00:00")
    small_repo.insert(r4)

    assert small_repo.count() == 3
    assert small_repo.find_by_id(r1.id) is None  # oldest evicted
    assert small_repo.find_by_id(r4.id) is not None  # new record kept


def test_insert_does_not_evict_saved_records(small_repo: TinyDBFactHistoryRepository) -> None:
    r1 = _make_record(text="saved-old", shown_at="2026-04-25T08:00:00")
    r2 = _make_record(text="saved-mid", shown_at="2026-04-25T09:00:00")
    r3 = _make_record(text="saved-new", shown_at="2026-04-25T10:00:00")
    for r in (r1, r2, r3):
        repo_insert = r
        small_repo.insert(repo_insert)
        small_repo.mark_saved(repo_insert.id)

    r4 = _make_record(text="new-fact", shown_at="2026-04-25T11:00:00")
    small_repo.insert(r4)  # all existing are saved — must exceed cap, not evict

    assert small_repo.count() == 4  # cap exceeded, no saved fact removed
    assert small_repo.find_by_id(r1.id) is not None  # saved facts preserved


def test_insert_evicts_oldest_non_saved_skipping_saved(small_repo: TinyDBFactHistoryRepository) -> None:
    r1 = _make_record(text="oldest-saved", shown_at="2026-04-25T08:00:00")
    r2 = _make_record(text="second-unsaved", shown_at="2026-04-25T09:00:00")
    r3 = _make_record(text="third-unsaved", shown_at="2026-04-25T10:00:00")
    small_repo.insert(r1)
    small_repo.mark_saved(r1.id)  # mark r1 as saved
    small_repo.insert(r2)
    small_repo.insert(r3)

    r4 = _make_record(text="new", shown_at="2026-04-25T11:00:00")
    small_repo.insert(r4)

    assert small_repo.count() == 3
    assert small_repo.find_by_id(r1.id) is not None  # saved — never evicted
    assert small_repo.find_by_id(r2.id) is None       # oldest non-saved evicted


# --- find_by_id ---

def test_find_by_id_returns_none_for_unknown_id(repo: TinyDBFactHistoryRepository) -> None:
    assert repo.find_by_id("nonexistent") is None


# --- mark_saved ---

def test_mark_saved_sets_saved_flag(repo: TinyDBFactHistoryRepository) -> None:
    r = _make_record()
    repo.insert(r)
    repo.mark_saved(r.id)
    found = repo.find_by_id(r.id)
    assert found is not None
    assert found.saved is True


# --- list_recent ---

def test_list_recent_returns_all_records_ordered_by_most_recent_first(
    repo: TinyDBFactHistoryRepository,
) -> None:
    r1 = _make_record(text="oldest", shown_at="2026-04-25T08:00:00")
    r2 = _make_record(text="newest", shown_at="2026-04-25T10:00:00")
    r3 = _make_record(text="middle", shown_at="2026-04-25T09:00:00")
    for r in (r1, r2, r3):
        repo.insert(r)

    results = repo.list_recent()
    assert results[0].text == "newest"
    assert results[1].text == "middle"
    assert results[2].text == "oldest"


def test_list_recent_filters_by_topic(repo: TinyDBFactHistoryRepository) -> None:
    repo.insert(_make_record(topic="Java", shown_at="2026-04-25T08:00:00"))
    repo.insert(_make_record(topic="Python", shown_at="2026-04-25T09:00:00"))
    repo.insert(_make_record(topic="Java", shown_at="2026-04-25T10:00:00"))

    results = repo.list_recent(topic="Java")
    assert len(results) == 2
    assert all(r.topic == "Java" for r in results)


def test_list_recent_returns_empty_when_no_records(repo: TinyDBFactHistoryRepository) -> None:
    assert repo.list_recent() == []


def test_list_recent_respects_limit(repo: TinyDBFactHistoryRepository) -> None:
    for i in range(5):
        repo.insert(_make_record(shown_at=f"2026-04-25T{8+i:02d}:00:00"))

    results = repo.list_recent(limit=3)
    assert len(results) == 3


# --- count ---

def test_count_returns_zero_initially(repo: TinyDBFactHistoryRepository) -> None:
    assert repo.count() == 0


def test_count_increases_after_insert(repo: TinyDBFactHistoryRepository) -> None:
    repo.insert(_make_record())
    repo.insert(_make_record())
    assert repo.count() == 2
