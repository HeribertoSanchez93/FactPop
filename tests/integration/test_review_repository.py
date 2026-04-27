import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.reviews.models import ReviewItem
from factpop.features.reviews.repository import TinyDBReviewRepository


@pytest.fixture
def repo() -> TinyDBReviewRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBReviewRepository(db.table("review_queue"))


def _item(fact_id: str = "f1", next_date: str = "2026-04-26") -> ReviewItem:
    import uuid
    return ReviewItem(
        id=str(uuid.uuid4()),
        fact_id=fact_id,
        fact_text="Java uses the JVM.",
        fact_topic="Java",
        next_review_date=next_date,
    )


def test_insert_and_find_by_fact_id(repo: TinyDBReviewRepository) -> None:
    item = _item("f1")
    repo.insert(item)
    found = repo.find_by_fact_id("f1")
    assert found is not None
    assert found.fact_id == "f1"


def test_find_by_fact_id_returns_none_when_not_found(repo: TinyDBReviewRepository) -> None:
    assert repo.find_by_fact_id("nonexistent") is None


def test_get_due_returns_item_due_today(repo: TinyDBReviewRepository) -> None:
    repo.insert(_item("f1", next_date="2026-04-25"))
    due = repo.get_due(as_of_date="2026-04-25")
    assert len(due) == 1
    assert due[0].fact_id == "f1"


def test_get_due_returns_item_overdue(repo: TinyDBReviewRepository) -> None:
    repo.insert(_item("f1", next_date="2026-04-20"))
    due = repo.get_due(as_of_date="2026-04-25")
    assert len(due) == 1


def test_get_due_excludes_future_items(repo: TinyDBReviewRepository) -> None:
    repo.insert(_item("f1", next_date="2026-04-30"))
    due = repo.get_due(as_of_date="2026-04-25")
    assert due == []


def test_get_due_excludes_resolved_items(repo: TinyDBReviewRepository) -> None:
    item = _item("f1", next_date="2026-04-25")
    repo.insert(item)
    item.resolved = True
    repo.update(item)
    due = repo.get_due(as_of_date="2026-04-25")
    assert due == []


def test_get_pending_returns_all_unresolved(repo: TinyDBReviewRepository) -> None:
    repo.insert(_item("f1", next_date="2026-04-25"))
    repo.insert(_item("f2", next_date="2026-04-30"))
    pending = repo.get_pending()
    assert len(pending) == 2


def test_get_pending_excludes_resolved(repo: TinyDBReviewRepository) -> None:
    item = _item("f1")
    repo.insert(item)
    item.resolved = True
    repo.update(item)
    assert repo.get_pending() == []


def test_update_persists_changes(repo: TinyDBReviewRepository) -> None:
    item = _item("f1", next_date="2026-04-25")
    repo.insert(item)
    item.fail_count = 3
    item.next_review_date = "2026-04-28"
    repo.update(item)
    found = repo.find_by_fact_id("f1")
    assert found.fail_count == 3
    assert found.next_review_date == "2026-04-28"


def test_count_pending(repo: TinyDBReviewRepository) -> None:
    repo.insert(_item("f1"))
    repo.insert(_item("f2"))
    assert repo.count_pending() == 2
