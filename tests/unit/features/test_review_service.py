import pytest
from freezegun import freeze_time
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.history.models import FactRecord
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService


def _make_record(fact_id: str = "f1", topic: str = "Java") -> FactRecord:
    return FactRecord(
        id=fact_id, topic=topic, text="Java uses the JVM.",
        shown_at="2026-04-25T10:00:00",
    )


@pytest.fixture
def service() -> ReviewService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBReviewRepository(db.table("review_queue"))
    return ReviewService(repo)


# --- enqueue ---

@freeze_time("2026-04-25")
def test_enqueue_sets_next_review_date_to_tomorrow(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    due = service.get_due(as_of_date="2026-04-26")
    assert len(due) == 1
    assert due[0].next_review_date == "2026-04-26"


@freeze_time("2026-04-25")
def test_enqueue_sets_fail_count_to_one(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    pending = service.get_pending()
    assert pending[0].fail_count == 1


@freeze_time("2026-04-25")
def test_enqueue_same_fact_twice_uses_increment_fail(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.enqueue(_make_record("f1"))  # second fail
    pending = service.get_pending()
    assert len(pending) == 1
    assert pending[0].fail_count == 2
    assert pending[0].next_review_date == "2026-04-27"  # today + 2


@freeze_time("2026-04-25")
def test_enqueue_caps_at_seven_days(service: ReviewService) -> None:
    for _ in range(10):
        service.enqueue(_make_record("f1"))
    item = service.get_pending()[0]
    assert item.next_review_date == "2026-05-02"  # today + 7


# --- resolve ---

@freeze_time("2026-04-25")
def test_resolve_marks_item_as_resolved(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.resolve("f1")
    assert service.get_pending() == []


@freeze_time("2026-04-25")
def test_resolve_removes_from_due(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.resolve("f1")
    assert service.get_due(as_of_date="2026-04-26") == []


def test_resolve_nonexistent_fact_does_not_raise(service: ReviewService) -> None:
    service.resolve("nonexistent")  # must not raise


# --- get_due ---

@freeze_time("2026-04-25")
def test_get_due_returns_items_due_on_or_before_date(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.enqueue(_make_record("f2"))
    # Both have next_review_date = "2026-04-26"
    assert service.get_due(as_of_date="2026-04-26") != []
    assert service.get_due(as_of_date="2026-04-25") == []  # not due yet


@freeze_time("2026-04-25")
def test_get_due_returns_empty_when_no_items(service: ReviewService) -> None:
    assert service.get_due(as_of_date="2026-04-26") == []


# --- get_pending ---

@freeze_time("2026-04-25")
def test_get_pending_returns_all_unresolved(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.enqueue(_make_record("f2"))
    assert len(service.get_pending()) == 2


@freeze_time("2026-04-25")
def test_get_pending_excludes_resolved(service: ReviewService) -> None:
    service.enqueue(_make_record("f1"))
    service.resolve("f1")
    assert service.get_pending() == []
