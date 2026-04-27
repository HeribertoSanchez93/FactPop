import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.topics.errors import (
    DuplicateTopicError,
    EmptyTopicNameError,
    TopicNotFoundError,
)
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService


@pytest.fixture
def service() -> TopicService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBTopicRepository(db.table("topics"))
    return TopicService(repo)


# --- create ---

def test_create_returns_topic(service: TopicService) -> None:
    topic = service.create("Java")
    assert topic.name == "Java"
    assert topic.active is True


def test_create_strips_leading_and_trailing_whitespace(service: TopicService) -> None:
    topic = service.create("  Java  ")
    assert topic.name == "Java"


def test_create_rejects_empty_name(service: TopicService) -> None:
    with pytest.raises(EmptyTopicNameError):
        service.create("")


def test_create_rejects_whitespace_only_name(service: TopicService) -> None:
    with pytest.raises(EmptyTopicNameError):
        service.create("   ")


def test_create_rejects_duplicate_name(service: TopicService) -> None:
    service.create("Java")
    with pytest.raises(DuplicateTopicError):
        service.create("Java")


def test_create_duplicate_check_is_case_insensitive(service: TopicService) -> None:
    service.create("Java")
    with pytest.raises(DuplicateTopicError):
        service.create("java")
    with pytest.raises(DuplicateTopicError):
        service.create("JAVA")


# --- list_all ---

def test_list_all_returns_empty_list_when_no_topics(service: TopicService) -> None:
    assert service.list_all() == []


def test_list_all_returns_all_topics(service: TopicService) -> None:
    service.create("Java")
    service.create("Python")
    assert len(service.list_all()) == 2


# --- list_active ---

def test_list_active_returns_only_active_topics(service: TopicService) -> None:
    service.create("Java")
    service.create("Python")
    service.deactivate("Python")
    active = service.list_active()
    assert len(active) == 1
    assert active[0].name == "Java"


def test_list_active_returns_empty_when_all_inactive(service: TopicService) -> None:
    service.create("Java")
    service.deactivate("Java")
    assert service.list_active() == []


# --- activate ---

def test_activate_sets_topic_to_active(service: TopicService) -> None:
    service.create("Java")
    service.deactivate("Java")
    topic = service.activate("Java")
    assert topic.active is True


def test_activate_nonexistent_topic_raises_error(service: TopicService) -> None:
    with pytest.raises(TopicNotFoundError):
        service.activate("NonExistent")


# --- deactivate ---

def test_deactivate_sets_topic_to_inactive(service: TopicService) -> None:
    service.create("Java")
    topic, _ = service.deactivate("Java")
    assert topic.active is False


def test_deactivate_returns_is_last_true_when_only_active_topic(service: TopicService) -> None:
    service.create("Java")
    _, is_last = service.deactivate("Java")
    assert is_last is True


def test_deactivate_returns_is_last_false_when_other_active_topics_exist(service: TopicService) -> None:
    service.create("Java")
    service.create("Python")
    _, is_last = service.deactivate("Java")
    assert is_last is False


def test_deactivate_nonexistent_topic_raises_error(service: TopicService) -> None:
    with pytest.raises(TopicNotFoundError):
        service.deactivate("NonExistent")


def test_deactivate_already_inactive_topic_raises_error(service: TopicService) -> None:
    service.create("Java")
    service.deactivate("Java")
    with pytest.raises(TopicNotFoundError):
        service.deactivate("NonExistent")


# --- delete ---

def test_delete_removes_topic_from_list(service: TopicService) -> None:
    service.create("Java")
    service.delete("Java")
    assert service.list_all() == []


def test_delete_nonexistent_topic_raises_error(service: TopicService) -> None:
    with pytest.raises(TopicNotFoundError):
        service.delete("NonExistent")


def test_delete_is_case_insensitive(service: TopicService) -> None:
    service.create("Java")
    service.delete("java")
    assert service.list_all() == []
