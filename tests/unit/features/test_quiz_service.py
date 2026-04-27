import pytest
from freezegun import freeze_time
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository
from factpop.features.quizzes.service import QuizService
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService
from factpop.shared.llm.fake import FakeLLMClient

_VALID_QUIZ_RESPONSE = (
    "QUESTION: What mechanism does Java use to manage memory?\n"
    "A: Manual deallocation\n"
    "B: Garbage collection\n"
    "C: Reference counting\n"
    "D: Stack-only allocation\n"
    "CORRECT: B"
)


def _setup(llm_response: str = _VALID_QUIZ_RESPONSE):
    db = TinyDB(storage=MemoryStorage)
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))
    attempt_repo = TinyDBQuizAttemptRepository(db.table("quiz_attempts"))
    llm = FakeLLMClient(response=llm_response)
    svc = QuizService(
        history_service=history_svc,
        review_service=review_svc,
        llm=llm,
        attempt_repo=attempt_repo,
    )
    return history_svc, review_svc, attempt_repo, llm, svc


def _populate_history(history_svc: FactHistoryService, count: int = 3) -> list:
    records = []
    for i in range(count):
        r = history_svc.record(topic="Java", text=f"Java fact number {i}.")
        records.append(r)
    return records


# --- generate: insufficient history ---

def test_generate_returns_none_when_fewer_than_3_facts() -> None:
    _, _, _, _, svc = _setup()
    # 0 facts in history
    assert svc.generate() is None


def test_generate_returns_none_with_exactly_2_facts() -> None:
    history_svc, _, _, _, svc = _setup()
    history_svc.record(topic="Java", text="Fact 1.")
    history_svc.record(topic="Java", text="Fact 2.")
    assert svc.generate() is None


def test_generate_does_not_call_llm_when_insufficient_history() -> None:
    _, _, _, llm, svc = _setup()
    svc.generate()
    assert llm.call_count == 0


# --- generate: normal path ---

def test_generate_returns_quiz_when_3_facts_exist() -> None:
    history_svc, _, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    assert quiz is not None


def test_generate_quiz_has_four_options() -> None:
    history_svc, _, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    assert quiz is not None
    assert len(quiz.options) == 4


def test_generate_prompt_includes_source_fact_text() -> None:
    history_svc, _, _, llm, svc = _setup()
    _populate_history(history_svc, 3)
    svc.generate()
    assert llm.last_prompt is not None
    assert "Java fact" in llm.last_prompt


# --- generate: review queue prioritization ---

@freeze_time("2026-04-26")
def test_generate_uses_review_item_when_due() -> None:
    history_svc, review_svc, _, llm, svc = _setup()
    records = _populate_history(history_svc, 3)
    # Enqueue the first fact as a review item due today
    with freeze_time("2026-04-25"):
        review_svc.enqueue(records[0])  # next_review_date = 2026-04-26

    quiz = svc.generate(as_of_date="2026-04-26")
    assert quiz is not None
    assert quiz.from_review_queue is True
    assert quiz.source_fact.id == records[0].id


@freeze_time("2026-04-25")
def test_generate_does_not_use_review_item_before_due_date() -> None:
    history_svc, review_svc, _, _, svc = _setup()
    records = _populate_history(history_svc, 3)
    review_svc.enqueue(records[0])  # due: 2026-04-26
    quiz = svc.generate(as_of_date="2026-04-25")
    assert quiz is not None
    assert quiz.from_review_queue is False


# --- grade: correct ---

def test_grade_correct_returns_true() -> None:
    history_svc, _, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    assert quiz is not None
    is_correct, _ = svc.grade(quiz, selected_index=quiz.correct_index)
    assert is_correct is True


def test_grade_correct_records_attempt_as_correct() -> None:
    history_svc, _, attempt_repo, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    svc.grade(quiz, selected_index=quiz.correct_index)
    attempts = attempt_repo.find_by_fact_id(quiz.source_fact.id)
    assert len(attempts) == 1
    assert attempts[0].is_correct is True


def test_grade_correct_on_review_item_resolves_it() -> None:
    history_svc, review_svc, _, _, svc = _setup()
    records = _populate_history(history_svc, 3)
    with freeze_time("2026-04-25"):
        review_svc.enqueue(records[0])
    quiz = svc.generate(as_of_date="2026-04-26")
    svc.grade(quiz, selected_index=quiz.correct_index)
    assert review_svc.get_pending() == []


# --- grade: incorrect ---

def test_grade_incorrect_returns_false() -> None:
    history_svc, _, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    wrong_index = (quiz.correct_index + 1) % 4
    is_correct, _ = svc.grade(quiz, selected_index=wrong_index)
    assert is_correct is False


def test_grade_incorrect_records_attempt_as_incorrect() -> None:
    history_svc, _, attempt_repo, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    wrong_index = (quiz.correct_index + 1) % 4
    svc.grade(quiz, selected_index=wrong_index)
    attempts = attempt_repo.find_by_fact_id(quiz.source_fact.id)
    assert attempts[0].is_correct is False


@freeze_time("2026-04-25")
def test_grade_incorrect_on_new_fact_enqueues_to_review() -> None:
    history_svc, review_svc, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    assert quiz.from_review_queue is False
    wrong_index = (quiz.correct_index + 1) % 4
    svc.grade(quiz, selected_index=wrong_index)
    assert len(review_svc.get_pending()) == 1


@freeze_time("2026-04-25")
def test_grade_incorrect_on_review_item_increments_fail() -> None:
    history_svc, review_svc, _, _, svc = _setup()
    records = _populate_history(history_svc, 3)
    review_svc.enqueue(records[0])  # fail_count = 1, next = 2026-04-26
    quiz = svc.generate(as_of_date="2026-04-26")
    wrong_index = (quiz.correct_index + 1) % 4
    svc.grade(quiz, selected_index=wrong_index)
    pending = review_svc.get_pending()
    assert pending[0].fail_count == 2
    assert pending[0].next_review_date == "2026-04-27"  # today + 2


# --- skip ---

def test_skip_does_not_record_attempt() -> None:
    history_svc, _, attempt_repo, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    svc.skip(quiz)
    assert attempt_repo.count() == 0


@freeze_time("2026-04-25")
def test_skip_does_not_add_to_review_queue() -> None:
    history_svc, review_svc, _, _, svc = _setup()
    _populate_history(history_svc, 3)
    quiz = svc.generate()
    svc.skip(quiz)
    assert review_svc.get_pending() == []
