from __future__ import annotations

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class SecretStore(Protocol):
    """Read-only access to secrets (API keys, credentials)."""

    def get(self, key: str, default: str | None = None) -> str | None:
        ...


class DotenvSecretStore:
    """Reads secrets from os.environ (populated by load_dotenv() at startup)."""

    def get(self, key: str, default: str | None = None) -> str | None:
        value = os.environ.get(key)
        if value is None or value == "":
            return default
        return value


class InMemorySecretStore:
    """Dict-backed secret store — used in tests to avoid real credentials."""

    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets

    def get(self, key: str, default: str | None = None) -> str | None:
        value = self._secrets.get(key)
        if value is None or value == "":
            return default
        return value
