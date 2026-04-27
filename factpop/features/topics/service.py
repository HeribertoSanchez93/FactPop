from __future__ import annotations

from factpop.features.topics.errors import (
    DuplicateTopicError,
    EmptyTopicNameError,
    TopicNotFoundError,
)
from factpop.features.topics.models import Topic
from factpop.features.topics.repository import TinyDBTopicRepository


class TopicService:
    def __init__(self, repo: TinyDBTopicRepository) -> None:
        self._repo = repo

    def create(self, name: str) -> Topic:
        name = name.strip()
        if not name:
            raise EmptyTopicNameError("Topic name must not be empty.")
        if self._repo.find_by_name(name) is not None:
            raise DuplicateTopicError(f"Topic '{name}' already exists.")
        return self._repo.create(name)

    def list_all(self) -> list[Topic]:
        return self._repo.list_all()

    def list_active(self) -> list[Topic]:
        return self._repo.list_active()

    def activate(self, name: str) -> Topic:
        topic = self._repo.find_by_name(name)
        if topic is None:
            raise TopicNotFoundError(f"Topic '{name}' not found.")
        topic.active = True
        self._repo.save(topic)
        return topic

    def deactivate(self, name: str) -> tuple[Topic, bool]:
        """Deactivate a topic.

        Returns:
            (topic, is_last_active) — is_last_active is True when no active
            topics remain after this deactivation.
        """
        topic = self._repo.find_by_name(name)
        if topic is None:
            raise TopicNotFoundError(f"Topic '{name}' not found.")
        topic.active = False
        self._repo.save(topic)
        is_last = len(self._repo.list_active()) == 0
        return topic, is_last

    def delete(self, name: str) -> None:
        topic = self._repo.find_by_name(name)
        if topic is None:
            raise TopicNotFoundError(f"Topic '{name}' not found.")
        self._repo.delete(topic.id)
