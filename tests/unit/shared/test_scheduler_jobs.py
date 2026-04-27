"""Tests for fact_job and quiz_job factory functions."""
from datetime import datetime

import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.notifications.null import NullDispatcher
from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository
from factpop.features.quizzes.service import QuizService
from factpop.features.reviews.repository import TinyDBReviewRepository
from factpop.features.reviews.service import ReviewService
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.llm.errors import LLMError
from factpop.shared.llm.fake import FakeLLMClient
from factpop.features.facts.service import FactService
from factpop.shared.scheduler.jobs import make_fact_job, make_quiz_job
from factpop.shared.scheduler.popup_state import PopupState
from factpop.features.quizzes.quiz_dispatcher import NullQuizDispatcher


_VALID_QUIZ_LLM = (
    "QUESTION: What does Java use for memory?\n"
    "A: Manual deallocation\nB: Garbage collection\n"
    "C: Reference counting\nD: Stack-only\nCORRECT: B"
)


def _setup_fact(llm_response: str = "FACT: Java uses the JVM."):
    db = TinyDB(storage=MemoryStorage)
    topic_svc = TopicService(TinyDBTopicRepository(db.table("topics")))
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    llm = FakeLLMClient(response=llm_response)
    fact_svc = FactService(topic_service=topic_svc, history_service=history_svc, llm=llm)
    return topic_svc, history_svc, fact_svc, llm


def _setup_quiz(llm_response: str = _VALID_QUIZ_LLM):
    db = TinyDB(storage=MemoryStorage)
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))
    attempt_repo = TinyDBQuizAttemptRepository(db.table("quiz_attempts"))
    llm = FakeLLMClient(response=llm_response)
    quiz_svc = QuizService(
        history_service=history_svc,
        review_service=review_svc,
        llm=llm,
        attempt_repo=attempt_repo,
    )
    return history_svc, quiz_svc


# ── fact_job ──────────────────────────────────────────────────────────────

def test_fact_job_calls_generate_and_record() -> None:
    topic_svc, history_svc, fact_svc, _ = _setup_fact()
    topic_svc.create("Java")
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()

    assert history_svc.count() == 1


def test_fact_job_calls_dispatcher_show_fact() -> None:
    topic_svc, history_svc, fact_svc, _ = _setup_fact()
    topic_svc.create("Java")
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()

    assert dispatcher.shown_count == 1


def test_fact_job_passes_correct_record_to_dispatcher() -> None:
    topic_svc, history_svc, fact_svc, _ = _setup_fact()
    topic_svc.create("Java")
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()

    assert dispatcher.last_record is not None
    assert dispatcher.last_record.topic == "Java"


def test_fact_job_does_not_show_popup_when_no_active_topics() -> None:
    _, history_svc, fact_svc, _ = _setup_fact()
    # no topics created
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()

    assert dispatcher.shown_count == 0


def test_fact_job_does_not_show_popup_on_llm_error() -> None:
    topic_svc, history_svc, fact_svc, _ = _setup_fact()
    topic_svc.create("Java")
    # Override llm to raise error
    from factpop.features.facts.service import FactService
    from tinydb import TinyDB
    from tinydb.storages import MemoryStorage
    db2 = TinyDB(storage=MemoryStorage)
    llm_err = FakeLLMClient(error=LLMError("api error"))
    fact_svc_err = FactService(
        topic_service=topic_svc,
        history_service=history_svc,
        llm=llm_err,
    )
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc_err, dispatcher, history_svc, popup_state)
    job()

    assert dispatcher.shown_count == 0


def test_fact_job_on_save_callback_marks_fact_saved() -> None:
    topic_svc, history_svc, fact_svc, _ = _setup_fact()
    topic_svc.create("Java")
    dispatcher = NullDispatcher()
    popup_state = PopupState()

    job = make_fact_job(fact_svc, dispatcher, history_svc, popup_state)
    job()
    dispatcher.trigger_save()

    recent = history_svc.get_recent(limit=1)
    assert recent[0].saved is True


# ── quiz_job ──────────────────────────────────────────────────────────────

def test_quiz_job_generates_and_shows_when_enough_history() -> None:
    history_svc, quiz_svc = _setup_quiz()
    for i in range(3):
        history_svc.record("Java", f"Java fact {i}.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()

    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=None)
    job()

    assert quiz_disp.shown_count == 1


def test_quiz_job_skips_when_insufficient_history() -> None:
    history_svc, quiz_svc = _setup_quiz()
    # only 2 facts

    history_svc.record("Java", "Fact 1.")
    history_svc.record("Java", "Fact 2.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()

    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=None)
    job()

    assert quiz_disp.shown_count == 0


def test_quiz_job_does_not_show_when_popup_is_active() -> None:
    history_svc, quiz_svc = _setup_quiz()
    for i in range(3):
        history_svc.record("Java", f"Fact {i}.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()
    popup_state.set_active()  # a fact popup is currently showing

    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=None)
    job()

    assert quiz_disp.shown_count == 0


def test_quiz_job_defers_via_runner_when_popup_active() -> None:
    from factpop.shared.scheduler.job_scheduler import FakeScheduleRunner
    history_svc, quiz_svc = _setup_quiz()
    for i in range(3):
        history_svc.record("Java", f"Fact {i}.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()
    popup_state.set_active()
    fake_runner = FakeScheduleRunner()

    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=fake_runner)
    job()

    assert len(fake_runner.once_jobs) == 1  # rescheduled once
    deferred_at = fake_runner.once_jobs[0][0]
    assert isinstance(deferred_at, datetime)


def test_quiz_job_on_submit_grades_quiz() -> None:
    history_svc, quiz_svc = _setup_quiz()
    for i in range(3):
        history_svc.record("Java", f"Fact {i}.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()
    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=None)
    job()

    # Trigger submit with correct answer (index 1 = B = "Garbage collection")
    quiz_disp.trigger_submit(quiz_disp.last_quiz.correct_index)
    # Attempt should be recorded
    assert quiz_svc._attempts.count() == 1


def test_quiz_job_on_skip_records_no_attempt() -> None:
    history_svc, quiz_svc = _setup_quiz()
    for i in range(3):
        history_svc.record("Java", f"Fact {i}.")

    quiz_disp = NullQuizDispatcher()
    popup_state = PopupState()
    job = make_quiz_job(quiz_svc, quiz_disp, popup_state, defer_runner=None)
    job()

    quiz_disp.trigger_skip()
    assert quiz_svc._attempts.count() == 0
