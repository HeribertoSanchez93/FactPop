from factpop.shared.llm.fake import FakeLLMClient


def test_fake_client_returns_configured_response() -> None:
    client = FakeLLMClient(response="Hello world")
    assert client.generate("any prompt") == "Hello world"


def test_fake_client_default_response_is_non_empty() -> None:
    client = FakeLLMClient()
    result = client.generate("any prompt")
    assert isinstance(result, str)
    assert len(result) > 0


def test_fake_client_records_last_prompt() -> None:
    client = FakeLLMClient()
    client.generate("test prompt")
    assert client.last_prompt == "test prompt"


def test_fake_client_records_call_count() -> None:
    client = FakeLLMClient()
    client.generate("first")
    client.generate("second")
    assert client.call_count == 2


def test_fake_client_records_all_prompts() -> None:
    client = FakeLLMClient()
    client.generate("prompt one")
    client.generate("prompt two")
    assert client.prompts_received == ["prompt one", "prompt two"]


def test_fake_client_accepts_model_kwarg() -> None:
    client = FakeLLMClient(response="ok")
    result = client.generate("prompt", model="gpt-4")
    assert result == "ok"


def test_fake_client_can_be_configured_to_raise() -> None:
    from factpop.shared.llm.errors import LLMError
    import pytest

    client = FakeLLMClient(error=LLMError("simulated failure"))
    with pytest.raises(LLMError, match="simulated failure"):
        client.generate("any prompt")
