# `factpop/shared/llm/cli.py` — `factpop-cli llm ping`

**Propósito:** Comando de diagnóstico para verificar que la conexión al LLM funciona correctamente. Se usa en el gate de aceptación y cuando el usuario quiere confirmar que su `.env` está bien configurado.

```python
def _build_client() -> LLMClient:
    return OpenAICompatibleClient(DotenvSecretStore())
```

`_build_client` es una función separada (no inline en el comando) para que los tests puedan reemplazarla con `monkeypatch.setattr`. Esto es el único punto donde `DotenvSecretStore` se instancia en el CLI — un único lugar de cambio si en el futuro se cambia la implementación de secretos.

```python
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
```

- El prompt `"Reply with exactly one word: pong"` es determinístico y fácil de verificar.
- Captura `LLMError` (la base de todos los errores LLM) — incluyendo auth, timeout y response.
- En caso de error: mensaje a stderr + exit code 1.

**Resultado con `.env` configurado:**
```
Sending test prompt to LLM...
Response: Pong
```

**Resultado sin API key:**
```
Sending test prompt to LLM...
Error: FACTPOP_API_KEY is not set. Add it to your .env file.
```

## ¿Por qué el CLI está en `shared/llm/` y no en `features/`?

El LLM es infraestructura compartida — lo usan tanto facts (Etapa 5) como quizzes (Etapa 8). No pertenece a ningún feature específico. El comando `ping` es una utilidad de diagnóstico de esa infraestructura, no una operación de negocio.
