import uuid

import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.quizzes.models import QuizAttempt
from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository


@pytest.fixture
def repo() -> TinyDBQuizAttemptRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBQuizAttemptRepository(db.table("quiz_attempts"))


def _attempt(fact_id: str = "f1", is_correct: bool = True) -> QuizAttempt:
    return QuizAttempt(
        id=str(uuid.uuid4()),
        fact_id=fact_id,
        question="What does Java use for memory?",
        selected_answer="Garbage collection",
        correct_answer="Garbage collection",
        is_correct=is_correct,
        attempted_at="2026-04-25T10:00:00",
    )


def test_insert_and_count(repo: TinyDBQuizAttemptRepository) -> None:
    repo.insert(_attempt())
    assert repo.count() == 1


def test_insert_multiple_increments_count(repo: TinyDBQuizAttemptRepository) -> None:
    repo.insert(_attempt("f1"))
    repo.insert(_attempt("f2"))
    assert repo.count() == 2


def test_count_zero_initially(repo: TinyDBQuizAttemptRepository) -> None:
    assert repo.count() == 0


def test_find_by_fact_id_returns_attempts(repo: TinyDBQuizAttemptRepository) -> None:
    repo.insert(_attempt("f1"))
    repo.insert(_attempt("f1", is_correct=False))
    repo.insert(_attempt("f2"))
    results = repo.find_by_fact_id("f1")
    assert len(results) == 2
    assert all(a.fact_id == "f1" for a in results)


def test_find_by_fact_id_returns_empty_for_unknown(repo: TinyDBQuizAttemptRepository) -> None:
    assert repo.find_by_fact_id("nonexistent") == []


def test_attempt_preserves_all_fields(repo: TinyDBQuizAttemptRepository) -> None:
    a = _attempt("f1", is_correct=False)
    a.selected_answer = "Manual deallocation"
    repo.insert(a)
    found = repo.find_by_fact_id("f1")[0]
    assert found.selected_answer == "Manual deallocation"
    assert found.correct_answer == "Garbage collection"
    assert found.is_correct is False
