from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from factpop.features.facts.service import FactService
from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.llm.errors import LLMError, LLMTimeoutError
from factpop.shared.llm.fake import FakeLLMClient


def _make_db():
    return TinyDB(storage=MemoryStorage)


def _setup(llm: FakeLLMClient, dedupe_window: int = 10):
    db = _make_db()
    topic_service = TopicService(TinyDBTopicRepository(db.table("topics")))
    history_service = FactHistoryService(
        TinyDBFactHistoryRepository(db.table("fact_history"))
    )
    fact_service = FactService(
        topic_service=topic_service,
        history_service=history_service,
        llm=llm,
        dedupe_window=dedupe_window,
    )
    return topic_service, history_service, fact_service


# --- topic selection ---

def test_returns_none_when_no_active_topics() -> None:
    llm = FakeLLMClient(response="FACT: some fact.")
    _, _, svc = _setup(llm)
    result = svc.generate_and_record()
    assert result is None


def test_does_not_call_llm_when_no_active_topics() -> None:
    llm = FakeLLMClient(response="FACT: some fact.")
    _, _, svc = _setup(llm)
    svc.generate_and_record()
    assert llm.call_count == 0


def test_selects_the_only_active_topic() -> None:
    llm = FakeLLMClient(response="FACT: Java uses the JVM.")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is not None
    assert result.topic == "Java"


def test_selected_topic_is_always_from_active_set() -> None:
    llm = FakeLLMClient(response="FACT: A learning fact.")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")
    topic_svc.create("Python")
    topic_svc.create("Kafka")

    active_names = {"Java", "Python", "Kafka"}
    for _ in range(20):
        result = svc.generate_and_record()
        assert result is not None
        assert result.topic in active_names


def test_uses_explicitly_provided_topic_name() -> None:
    llm = FakeLLMClient(response="FACT: Python uses indentation.")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")
    topic_svc.create("Python")

    result = svc.generate_and_record(topic_name="Python")
    assert result is not None
    assert result.topic == "Python"


# --- LLM call and response ---

def test_generates_and_records_fact_on_success() -> None:
    llm = FakeLLMClient(response="FACT: Java uses garbage collection.")
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is not None
    assert result.text == "Java uses garbage collection."
    assert history_svc.count() == 1


def test_fact_includes_example_when_llm_provides_one() -> None:
    llm = FakeLLMClient(response="FACT: Java uses generics.\nEXAMPLE: List<String> names;")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is not None
    assert result.example == "List<String> names;"


def test_returns_none_on_llm_error() -> None:
    llm = FakeLLMClient(error=LLMTimeoutError("timeout"))
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is None


def test_does_not_save_to_history_on_llm_error() -> None:
    llm = FakeLLMClient(error=LLMError("api error"))
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Java")

    svc.generate_and_record()
    assert history_svc.count() == 0


def test_returns_none_on_empty_llm_response() -> None:
    llm = FakeLLMClient(response="")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is None


def test_does_not_save_to_history_on_empty_response() -> None:
    llm = FakeLLMClient(response="   ")
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Java")

    svc.generate_and_record()
    assert history_svc.count() == 0


# --- deduplication ---

def test_retries_once_when_fact_is_similar_to_recent_history() -> None:
    first = "FACT: Java uses garbage collection to manage memory."
    similar = "FACT: Java uses garbage collection for memory management."
    different = "FACT: Java supports multiple inheritance via interfaces."

    # First call returns similar text, second returns different
    responses = [first, similar, different]
    call_index = 0

    class SequencedFakeLLM:
        call_count = 0
        last_prompt = None
        prompts_received = []

        def generate(self, prompt: str, *, model: str | None = None) -> str:  # noqa: ARG002
            self.last_prompt = prompt
            self.prompts_received.append(prompt)
            self.call_count += 1
            nonlocal call_index
            r = responses[call_index % len(responses)]
            call_index += 1
            return r

    llm = SequencedFakeLLM()
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Java")

    # Pre-populate history with a similar fact
    history_svc.record("Java", "Java uses garbage collection to manage memory.")

    svc.generate_and_record()
    # Should have retried — at least 2 LLM calls total
    assert llm.call_count >= 2


def test_proceeds_after_two_similar_attempts() -> None:
    # Use strings that are genuinely near-duplicate (ratio >= 0.85) so the
    # dedup condition actually fires and we can assert exactly 2 LLM calls.
    original = "Java uses garbage collection to manage memory."
    similar1 = "FACT: Java uses garbage collection to manage memory."       # ratio ≈ 1.0
    similar2 = "FACT: Java uses garbage collection to handle memory."        # returned as-is

    responses = [similar1, similar2]
    call_index = 0

    class SequencedFakeLLM:
        call_count = 0
        last_prompt = None
        prompts_received = []

        def generate(self, prompt: str, *, model: str | None = None) -> str:  # noqa: ARG002
            self.last_prompt = prompt
            self.prompts_received.append(prompt)
            self.call_count += 1
            nonlocal call_index
            r = responses[call_index % len(responses)]
            call_index += 1
            return r

    llm = SequencedFakeLLM()
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Java")
    history_svc.record("Java", original)

    result = svc.generate_and_record()
    # Must not retry more than once — result is returned even if similar
    assert llm.call_count == 2
    assert result is not None  # proceeds with second attempt
    assert history_svc.count() == 2


def test_no_dedup_check_when_topic_has_no_history() -> None:
    llm = FakeLLMClient(response="FACT: Java uses the JVM.")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Java")

    result = svc.generate_and_record()
    assert result is not None
    assert llm.call_count == 1  # no retry needed


# --- history persistence ---

def test_saved_fact_record_has_correct_topic() -> None:
    llm = FakeLLMClient(response="FACT: Python is interpreted.")
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Python")

    result = svc.generate_and_record()
    assert result is not None
    recent = history_svc.get_recent()
    assert recent[0].topic == "Python"


def test_saved_fact_record_has_generated_text() -> None:
    llm = FakeLLMClient(response="FACT: Python is interpreted.")
    topic_svc, history_svc, svc = _setup(llm)
    topic_svc.create("Python")

    svc.generate_and_record()
    recent = history_svc.get_recent()
    assert recent[0].text == "Python is interpreted."


def test_prompt_includes_topic_name() -> None:
    llm = FakeLLMClient(response="FACT: Kafka is distributed.")
    topic_svc, _, svc = _setup(llm)
    topic_svc.create("Kafka")

    svc.generate_and_record()
    assert llm.last_prompt is not None
    assert "Kafka" in llm.last_prompt
