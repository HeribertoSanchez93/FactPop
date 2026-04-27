# `factpop/features/facts/cli.py`

```
factpop-cli facts generate [--topic TOPIC]
```

---

```python
def _build_llm() -> LLMClient:
    return OpenAICompatibleClient(DotenvSecretStore())
```

Función separada para que los tests puedan reemplazarla vía `monkeypatch.setattr("factpop.features.facts.cli._build_llm", ...)`. El mismo patrón usado en `shared/llm/cli.py`.

```python
def _build_service() -> FactService:
    db = get_db()
    ...
    return FactService(topic_service=..., history_service=..., llm=_build_llm())
```

El servicio se construye en la función del comando (no a nivel de módulo), para que `_build_llm` pueda ser reemplazado por monkeypatch antes de la construcción.

```python
result = svc.generate_and_record(topic_name=topic)
if result is None:
    typer.echo("Error: Could not generate...", err=True)
    raise typer.Exit(code=1)
```

`None` cubre todos los casos de falla (no topics, LLM error, respuesta vacía). El CLI no necesita distinguir cuál fue — el log ya lo registró.

```python
typer.echo(f"[{result.topic}] {result.text}")
if result.example:
    typer.echo(f"\nExample:\n{result.example}")
```

**Salida con topic genérico:**
```
[Java] In Java, StringBuilder is used for efficient string manipulation.

Example:
StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");
```

**Salida con topic específico:**
```
[AWS IAM - creacion de grupos de roles] In AWS IAM, roles can be assigned to groups...

Example:
{
  "Version": "2012-10-17",
  "Statement": [...]
}
```
