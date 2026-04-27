from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime

from factpop.features.history.models import FactRecord
from factpop.features.history.service import FactHistoryService
from factpop.features.quizzes.models import Quiz, QuizAttempt
from factpop.features.quizzes.prompts import build_quiz_prompt, parse_quiz_response
from factpop.features.quizzes.repository import TinyDBQuizAttemptRepository
from factpop.features.reviews.interfaces import ReviewScheduler
from factpop.features.reviews.models import ReviewItem
from factpop.shared.llm.client import LLMClient
from factpop.shared.llm.errors import LLMError

logger = logging.getLogger(__name__)
_MIN_HISTORY = 3


class QuizService:
    def __init__(
        self,
        history_service: FactHistoryService,
        review_service: ReviewScheduler,
        llm: LLMClient,
        attempt_repo: TinyDBQuizAttemptRepository,
        min_history: int = _MIN_HISTORY,
    ) -> None:
        self._history = history_service
        self._review = review_service
        self._llm = llm
        self._attempts = attempt_repo
        self._min_history = min_history

    def generate(self, as_of_date: str | None = None) -> Quiz | None:
        """Generate a quiz, prioritizing review-queue items due today."""
        recent = self._history.get_recent(limit=50)
        if len(recent) < self._min_history:
            logger.info("Insufficient history (%d facts) — skipping quiz.", len(recent))
            return None

        due_items = self._review.get_due(as_of_date=as_of_date)
        if due_items:
            source_fact, from_review = self._fact_from_review(due_items)
        else:
            source_fact = random.choice(recent)
            from_review = False

        quiz = self._generate_from_fact(source_fact)
        if quiz is None:
            return None

        quiz.from_review_queue = from_review
        return quiz

    def grade(self, quiz: Quiz, selected_index: int) -> tuple[bool, QuizAttempt]:
        """Grade the answer, persist the attempt, and update review queue."""
        is_correct = selected_index == quiz.correct_index
        selected_answer = quiz.options[selected_index]
        correct_answer = quiz.options[quiz.correct_index]

        attempt = QuizAttempt(
            id=str(uuid.uuid4()),
            fact_id=quiz.source_fact.id,
            question=quiz.question,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            attempted_at=datetime.now().isoformat(timespec="seconds"),
        )
        self._attempts.insert(attempt)

        if is_correct and quiz.from_review_queue:
            self._review.resolve(quiz.source_fact.id)
        elif not is_correct:
            if quiz.from_review_queue:
                self._review.increment_fail(quiz.source_fact.id)
            else:
                self._review.enqueue(quiz.source_fact)

        return is_correct, attempt

    def skip(self, quiz: Quiz) -> None:
        """Skip the quiz — no attempt recorded, no review queue changes."""

    # --- private ---

    def _fact_from_review(self, due_items: list[ReviewItem]) -> tuple[FactRecord, bool]:
        item = due_items[0]
        fact = FactRecord(
            id=item.fact_id,
            topic=item.fact_topic,
            text=item.fact_text,
            shown_at="",
        )
        return fact, True

    def _generate_from_fact(self, source_fact: FactRecord) -> Quiz | None:
        prompt = build_quiz_prompt(source_fact.text)
        try:
            raw = self._llm.generate(prompt)
        except LLMError as exc:
            logger.error("LLM error generating quiz: %s", exc)
            return None

        quiz = parse_quiz_response(raw, source_fact_text=source_fact.text)
        if quiz is None:
            logger.warning("Could not parse quiz response from LLM.")
            return None

        quiz.source_fact = source_fact
        return quiz
