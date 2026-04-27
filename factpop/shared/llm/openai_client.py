from __future__ import annotations

import openai

from factpop.features.settings.secrets import SecretStore
from factpop.shared.llm.errors import LLMAuthError, LLMResponseError, LLMTimeoutError

_DEFAULT_BASE_URL = "https://api.openai.com/v1"
_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_TIMEOUT = 20.0


class OpenAICompatibleClient:
    """LLM client that works with any OpenAI-compatible API endpoint.

    Reads FACTPOP_API_KEY, FACTPOP_BASE_URL, FACTPOP_MODEL, and
    FACTPOP_LLM_TIMEOUT_SECONDS from the provided SecretStore.
    """

    def __init__(self, secrets: SecretStore) -> None:
        self._secrets = secrets

    def generate(self, prompt: str, *, model: str | None = None) -> str:
        api_key = self._secrets.get("FACTPOP_API_KEY")
        if not api_key:
            raise LLMAuthError(
                "FACTPOP_API_KEY is not set. Add it to your .env file."
            )

        base_url = self._secrets.get("FACTPOP_BASE_URL") or _DEFAULT_BASE_URL
        model_name = model or self._secrets.get("FACTPOP_MODEL") or _DEFAULT_MODEL
        timeout = float(
            self._secrets.get("FACTPOP_LLM_TIMEOUT_SECONDS") or _DEFAULT_TIMEOUT
        )

        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise LLMResponseError("LLM returned an empty response.")
            return content.strip()
        except openai.AuthenticationError as exc:
            raise LLMAuthError(str(exc)) from exc
        except openai.APITimeoutError as exc:
            raise LLMTimeoutError(str(exc)) from exc
        except openai.APIError as exc:
            raise LLMResponseError(str(exc)) from exc
