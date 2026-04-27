from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Global scheduler service — stopped on shutdown
_scheduler_service = None


def bootstrap() -> None:
    """Wire all services and start the background scheduler."""
    from dotenv import load_dotenv

    from factpop.features.facts.service import FactService
    from factpop.features.history.repository import TinyDBFactHistoryRepository
    from factpop.features.history.service import FactHistoryService
    from factpop.features.notifications.null import NullDispatcher
    from factpop.features.quizzes.quiz_dispatcher import NullQuizDispatcher
    from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository
    from factpop.features.quizzes.service import QuizService
    from factpop.features.reviews.repository import TinyDBReviewRepository
    from factpop.features.reviews.service import ReviewService
    from factpop.features.settings.repository import TinyDBSettingsRepository
    from factpop.features.settings.secrets import DotenvSecretStore
    from factpop.features.settings.service import SettingsService
    from factpop.features.topics.repository import TinyDBTopicRepository
    from factpop.features.topics.service import TopicService
    from factpop.shared.llm.openai_client import OpenAICompatibleClient
    from factpop.shared.scheduler.clock import SystemClock
    from factpop.shared.scheduler.jobs import make_fact_job, make_quiz_job
    from factpop.shared.scheduler.popup_state import PopupState
    from factpop.shared.scheduler.schedule_runner import ScheduleRunner
    from factpop.shared.scheduler.service import SchedulerService
    from factpop.shared.storage.tinydb_factory import get_db

    db = get_db()

    # ── persistence layer ───────────────────────────────────────────────
    settings_svc = SettingsService(TinyDBSettingsRepository(db.table("app_config")))
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    review_svc = ReviewService(TinyDBReviewRepository(db.table("review_queue")))
    attempt_repo = TinyDBQuizAttemptRepository(db.table("quiz_attempts"))
    topic_svc = TopicService(TinyDBTopicRepository(db.table("topics")))

    # ── LLM + content ───────────────────────────────────────────────────
    llm = OpenAICompatibleClient(DotenvSecretStore())
    fact_svc = FactService(topic_service=topic_svc, history_service=history_svc, llm=llm)
    quiz_svc = QuizService(
        history_service=history_svc,
        review_service=review_svc,
        llm=llm,
        attempt_repo=attempt_repo,
    )

    # ── dispatchers ─────────────────────────────────────────────────────
    popup_state = PopupState()

    try:
        from factpop.features.notifications.tk_popup import TkPopupDispatcher
        fact_dispatcher = TkPopupDispatcher()
    except Exception:
        fact_dispatcher = NullDispatcher()

    try:
        from factpop.features.quizzes.tk_window import TkQuizDispatcher
        quiz_dispatcher = TkQuizDispatcher()
    except Exception:
        quiz_dispatcher = NullQuizDispatcher()

    # ── job functions ───────────────────────────────────────────────────
    runner = ScheduleRunner()
    fact_job = make_fact_job(fact_svc, fact_dispatcher, history_svc, popup_state)
    quiz_job = make_quiz_job(quiz_svc, quiz_dispatcher, popup_state, defer_runner=runner)

    # ── scheduler ───────────────────────────────────────────────────────
    global _scheduler_service
    _scheduler_service = SchedulerService(
        settings=settings_svc,
        runner=runner,
        fact_job=fact_job,
        quiz_job=quiz_job,
        clock=SystemClock(),
    )
    _scheduler_service.start()
    logger.info("Bootstrap complete — scheduler running.")


def shutdown() -> None:
    global _scheduler_service
    if _scheduler_service is not None:
        _scheduler_service.stop()
        _scheduler_service = None
