from factpop.features.history.models import FactRecord


def test_fact_record_requires_id_topic_text_and_shown_at() -> None:
    r = FactRecord(id="1", topic="Java", text="Java is compiled.", shown_at="2026-04-25T10:00:00")
    assert r.id == "1"
    assert r.topic == "Java"
    assert r.text == "Java is compiled."
    assert r.shown_at == "2026-04-25T10:00:00"


def test_fact_record_saved_defaults_to_false() -> None:
    r = FactRecord(id="1", topic="Java", text="some fact", shown_at="2026-04-25T10:00:00")
    assert r.saved is False


def test_fact_record_example_defaults_to_none() -> None:
    r = FactRecord(id="1", topic="Java", text="some fact", shown_at="2026-04-25T10:00:00")
    assert r.example is None


def test_fact_record_can_have_example() -> None:
    r = FactRecord(
        id="1", topic="Java", text="Java uses generics.",
        shown_at="2026-04-25T10:00:00", example="List<String> names = new ArrayList<>();"
    )
    assert r.example == "List<String> names = new ArrayList<>();"


def test_fact_record_can_be_marked_saved() -> None:
    r = FactRecord(id="1", topic="Java", text="fact", shown_at="2026-04-25T10:00:00", saved=True)
    assert r.saved is True
