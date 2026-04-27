import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.topics.repository import TinyDBTopicRepository


@pytest.fixture
def repo() -> TinyDBTopicRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBTopicRepository(db.table("topics"))


def test_create_returns_topic_with_name(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    assert topic.name == "Java"


def test_create_new_topic_is_active_by_default(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    assert topic.active is True


def test_create_generates_unique_ids(repo: TinyDBTopicRepository) -> None:
    t1 = repo.create("Java")
    t2 = repo.create("Python")
    assert t1.id != t2.id


def test_create_assigns_non_empty_id(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    assert topic.id is not None
    assert len(topic.id) > 0


def test_find_by_name_returns_existing_topic(repo: TinyDBTopicRepository) -> None:
    repo.create("Java")
    found = repo.find_by_name("Java")
    assert found is not None
    assert found.name == "Java"


def test_find_by_name_is_case_insensitive(repo: TinyDBTopicRepository) -> None:
    repo.create("Java")
    assert repo.find_by_name("java") is not None
    assert repo.find_by_name("JAVA") is not None
    assert repo.find_by_name("jAvA") is not None


def test_find_by_name_returns_none_when_not_found(repo: TinyDBTopicRepository) -> None:
    assert repo.find_by_name("NonExistent") is None


def test_list_all_returns_all_topics(repo: TinyDBTopicRepository) -> None:
    repo.create("Java")
    repo.create("Python")
    assert len(repo.list_all()) == 2


def test_list_all_returns_empty_list_when_no_topics(repo: TinyDBTopicRepository) -> None:
    assert repo.list_all() == []


def test_save_persists_active_flag_change(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    topic.active = False
    repo.save(topic)

    found = repo.find_by_name("Java")
    assert found is not None
    assert found.active is False


def test_save_persists_name_change(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    topic.name = "Java SE"
    repo.save(topic)

    assert repo.find_by_name("Java SE") is not None
    assert repo.find_by_name("Java") is None


def test_delete_removes_topic(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    repo.delete(topic.id)
    assert repo.find_by_name("Java") is None


def test_delete_nonexistent_id_does_not_raise(repo: TinyDBTopicRepository) -> None:
    repo.delete("nonexistent-id")  # must not raise


def test_find_by_id_returns_correct_topic(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    found = repo.find_by_id(topic.id)
    assert found is not None
    assert found.name == "Java"


def test_find_by_id_returns_none_when_not_found(repo: TinyDBTopicRepository) -> None:
    assert repo.find_by_id("nonexistent-id") is None


def test_list_active_returns_only_active_topics(repo: TinyDBTopicRepository) -> None:
    java = repo.create("Java")
    repo.create("Python")
    java.active = False
    repo.save(java)

    active = repo.list_active()
    assert len(active) == 1
    assert active[0].name == "Python"


def test_list_active_returns_empty_when_all_inactive(repo: TinyDBTopicRepository) -> None:
    topic = repo.create("Java")
    topic.active = False
    repo.save(topic)

    assert repo.list_active() == []
