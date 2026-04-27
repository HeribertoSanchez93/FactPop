# `factpop/features/history/cli.py`

**Propósito:** Permite al usuario consultar el historial de facts desde el terminal.

```
factpop-cli history list [--topic TOPIC] [--saved-only]
```

---

```python
@app.command("list")
def list_history(
    topic: Optional[str] = typer.Option(None, "--topic", help="Filter by topic name"),
    saved_only: bool = typer.Option(False, "--saved-only", help="Show only saved facts"),
) -> None:
```

- `--topic` es opcional (`None` por defecto) → sin el flag muestra todos los temas
- `--saved-only` es un flag booleano (`False` por defecto) → sin el flag muestra todos los estados

```python
    records = _service().get_recent(topic=topic, limit=200)
    if saved_only:
        records = [r for r in records if r.saved]
```

El filtro `saved_only` se aplica **en Python después de la query**, no en TinyDB. Esto es aceptable porque el límite de 200 es pequeño. Si en el futuro el historial crece mucho, se puede mover el filtro al repositorio.

```python
    for r in records:
        status = "[saved]" if r.saved else "      "
        example_hint = "  (has example)" if r.example else ""
        typer.echo(f"{status}  [{r.topic}]  {r.shown_at[:16]}  {r.text[:60]}{example_hint}")
```

- `"[saved]"` vs `"      "` — alinea los registros visualmente (6 chars cada uno)
- `r.shown_at[:16]` — muestra `"2026-04-25T10:00"` (sin segundos, más legible)
- `r.text[:60]` — trunca textos largos a 60 chars para que quepan en una línea
- `"  (has example)"` — indica si hay ejemplo disponible sin mostrarlo completo

**Salida de ejemplo:**
```
[saved]  [Java]  2026-04-25T14:47  Java uses garbage collection.  (has example)
        [Python]  2026-04-25T14:47  Python is interpreted.
        [Java]  2026-04-25T14:47  Java supports generics.
```
