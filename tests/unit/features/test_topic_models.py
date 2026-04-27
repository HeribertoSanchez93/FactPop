from factpop.features.topics.models import Topic


def test_topic_is_active_by_default() -> None:
    topic = Topic(id="1", name="Java")
    assert topic.active is True


def test_topic_can_be_created_inactive() -> None:
    topic = Topic(id="1", name="Java", active=False)
    assert topic.active is False


def test_topic_name_is_preserved() -> None:
    topic = Topic(id="1", name="Spring Boot")
    assert topic.name == "Spring Boot"


def test_topic_id_is_preserved() -> None:
    topic = Topic(id="abc-123", name="Java")
    assert topic.id == "abc-123"
