from __future__ import annotations

from factpop.shared.llm.errors import LLMError


class FakeLLMClient:
    """In-memory LLM client for tests.

    Can be configured to return a fixed response or raise a specific error.
    Records all prompts received for assertion in tests.
    """

    def __init__(
        self,
        response: str = "Fake LLM response.",
        error: LLMError | None = None,
    ) -> None:
        self._response = response
        self._error = error
        self.prompts_received: list[str] = []
        self.last_prompt: str | None = None
        self.call_count: int = 0

    def generate(self, prompt: str, *, model: str | None = None) -> str:
        self.prompts_received.append(prompt)
        self.last_prompt = prompt
        self.call_count += 1
        if self._error is not None:
            raise self._error
        return self._response
