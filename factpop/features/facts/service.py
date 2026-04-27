from __future__ import annotations

import logging
import random
from difflib import SequenceMatcher

from factpop.features.facts.prompts import build_fact_prompt, parse_llm_response
from factpop.features.history.models import FactRecord
from factpop.features.history.service import FactHistoryService
from factpop.features.topics.service import TopicService
from factpop.shared.llm.client import LLMClient
from factpop.shared.llm.errors import LLMError

logger = logging.getLogger(__name__)

_SIMILARITY_THRESHOLD = 0.85
_DEFAULT_DEDUPE_WINDOW = 10


def _is_similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= _SIMILARITY_THRESHOLD


class FactService:
    def __init__(
        self,
        topic_service: TopicService,
        history_service: FactHistoryService,
        llm: LLMClient,
        dedupe_window: int = _DEFAULT_DEDUPE_WINDOW,
    ) -> None:
        self._topics = topic_service
        self._history = history_service
        self._llm = llm
        self._dedupe_window = dedupe_window

    def generate_and_record(
        self, topic_name: str | None = None
    ) -> FactRecord | None:
        """Generate a fact for a topic and persist it.

        Returns None without calling the LLM when:
        - No active topics exist (and no topic_name given)
        - LLM raises an error
        - LLM returns empty/unparseable response
        """
        topic = self._resolve_topic(topic_name)
        if topic is None:
            logger.warning("No active topics available — skipping fact generation.")
            return None

        recent = self._history.get_recent(topic=topic, limit=self._dedupe_window)
        recent_texts = [r.text for r in recent]
        prompt = build_fact_prompt(topic, recent_texts=recent_texts or None)

        fact = self._call_llm_with_dedup(prompt, topic, recent_texts)
        if fact is None:
            return None

        return self._history.record(
            topic=topic,
            text=fact.text,
            example=fact.example,
        )

    # --- private helpers ---

    def _resolve_topic(self, topic_name: str | None) -> str | None:
        if topic_name is not None:
            return topic_name
        active = self._topics.list_active()
        if not active:
            return None
        return random.choice(active).name

    def _call_llm_with_dedup(
        self,
        prompt: str,
        topic: str,
        recent_texts: list[str],
    ):
        """Call LLM once; retry once if result is too similar to recent history."""
        raw = self._call_llm(prompt)
        if raw is None:
            return None

        fact = parse_llm_response(raw)
        if fact is None:
            logger.warning("LLM returned empty or unparseable response.")
            return None

        fact.topic = topic

        # Dedup check: retry once if similar to any recent fact
        if recent_texts and any(_is_similar(fact.text, t) for t in recent_texts):
            logger.info("Generated fact is similar to recent history — retrying once.")
            retry_raw = self._call_llm(prompt)
            if retry_raw is not None:
                retry_fact = parse_llm_response(retry_raw)
                if retry_fact is not None:
                    retry_fact.topic = topic
                    fact = retry_fact  # use second attempt regardless

        return fact

    def _call_llm(self, prompt: str) -> str | None:
        try:
            return self._llm.generate(prompt)
        except LLMError as exc:
            logger.error("LLM call failed: %s", exc)
            return None
