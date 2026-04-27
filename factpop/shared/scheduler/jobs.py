from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Callable

from factpop.features.facts.service import FactService
from factpop.features.history.service import FactHistoryService
from factpop.features.notifications.dispatcher import NotificationDispatcher
from factpop.features.quizzes.quiz_dispatcher import QuizDispatcher
from factpop.features.quizzes.service import QuizService
from factpop.shared.scheduler.popup_state import PopupState

logger = logging.getLogger(__name__)

_QUIZ_DEFER_MINUTES = 5


def make_fact_job(
    fact_svc: FactService,
    dispatcher: NotificationDispatcher,
    history_svc: FactHistoryService,
    popup_state: PopupState,
) -> Callable:
    """Return a callable that generates a fact and shows it via the dispatcher."""

    def _job() -> None:
        record = fact_svc.generate_and_record()
        if record is None:
            logger.info("fact_job: no fact generated (no active topics or LLM error).")
            return

        def on_save() -> None:
            history_svc.mark_saved(record.id)

        def on_show_another() -> None:
            _job()

        popup_state.set_active()
        try:
            dispatcher.show_fact(record, on_save=on_save, on_show_another=on_show_another)
        finally:
            popup_state.set_inactive()

    return _job


def make_quiz_job(
    quiz_svc: QuizService,
    quiz_dispatcher: QuizDispatcher,
    popup_state: PopupState,
    defer_runner,   # JobScheduler | None — None disables deferral (e.g. tests)
    defer_minutes: int = _QUIZ_DEFER_MINUTES,
) -> Callable:
    """Return a callable that generates a quiz, defers if a popup is active."""

    def _job() -> None:
        if popup_state.is_active():
            logger.info("quiz_job: fact popup active — deferring quiz by %d min.", defer_minutes)
            if defer_runner is not None:
                deferred_at = datetime.now() + timedelta(minutes=defer_minutes)
                defer_runner.add_once_at(deferred_at, _job, job_id="quiz-deferred")
            return

        quiz = quiz_svc.generate()
        if quiz is None:
            logger.info("quiz_job: no quiz generated (insufficient history).")
            return

        def on_submit(selected_index: int) -> None:
            quiz_svc.grade(quiz, selected_index=selected_index)

        def on_skip() -> None:
            quiz_svc.skip(quiz)

        popup_state.set_active()
        try:
            quiz_dispatcher.show_quiz(quiz, on_submit=on_submit, on_skip=on_skip)
        finally:
            popup_state.set_inactive()

    return _job
