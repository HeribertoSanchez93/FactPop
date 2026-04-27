from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Minimal interface for any LLM provider.

    Implementations: OpenAICompatibleClient (production), FakeLLMClient (tests).
    """

    def generate(self, prompt: str, *, model: str | None = None) -> str:
        """Send a prompt and return the model's text response.

        Raises:
            LLMAuthError: API key missing or rejected.
            LLMTimeoutError: Request exceeded timeout.
            LLMResponseError: Empty or malformed response.
        """
        ...
