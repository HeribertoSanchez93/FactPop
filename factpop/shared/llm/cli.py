from __future__ import annotations

import typer

from factpop.features.settings.secrets import DotenvSecretStore
from factpop.shared.llm.client import LLMClient
from factpop.shared.llm.errors import LLMError
from factpop.shared.llm.openai_client import OpenAICompatibleClient

app = typer.Typer(help="LLM connection utilities.")


def _build_client() -> LLMClient:
    return OpenAICompatibleClient(DotenvSecretStore())


@app.command("ping")
def ping() -> None:
    """Send a test prompt to the configured LLM and print the response."""
    client = _build_client()
    try:
        typer.echo("Sending test prompt to LLM...")
        response = client.generate("Reply with exactly one word: pong")
        typer.echo(f"Response: {response}")
    except LLMError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
