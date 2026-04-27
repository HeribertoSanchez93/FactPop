from factpop.shared.errors import FactPopError


class LLMError(FactPopError):
    """Base class for all LLM-related errors."""


class LLMAuthError(LLMError):
    """Raised when the API key is missing or rejected by the provider."""


class LLMTimeoutError(LLMError):
    """Raised when the LLM API call exceeds the configured timeout."""


class LLMResponseError(LLMError):
    """Raised when the LLM returns an empty, malformed, or unexpected response."""
