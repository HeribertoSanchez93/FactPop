# CLI de Etapa 8

## Refactoring del grupo `quiz`

En Stage 3, `quiz toggle` vivía en `features/settings/cli.py` y se registraba como `quiz`. En Stage 8, ese comando se **movió** a `features/quizzes/cli.py` junto con el nuevo `simulate`, para tener todos los comandos de quiz en un solo módulo.

`app/cli.py` ahora registra:
```python
app.add_typer(quizzes_cli.app, name="quiz")   # toggle + simulate
app.add_typer(reviews_cli.app, name="reviews")
```

Resultado:
```
factpop-cli
  quiz
    toggle on/off          ← antes en settings, ahora en quizzes
    simulate [--date]      ← nuevo
  reviews
    list                   ← nuevo
```

---

## `quiz simulate [--date DATE]`

```python
@app.command("simulate")
def simulate(
    date_override: Optional[str] = typer.Option(None, "--date", ...)
) -> None:
```

El `--date` flag permite sobreescribir "hoy" para probar la priorización de la review queue sin esperar al día siguiente:

```bash
# Responder mal, añade a queue con due: tomorrow
factpop-cli quiz simulate

# Al día siguiente (o forzando la fecha):
factpop-cli quiz simulate --date 2026-04-26
# → usa el item de review como fuente del quiz
```

**Flujo de simulate:**
1. `svc.generate(as_of_date)` → `Quiz | None`
2. Si `None` → "Not enough history..."
3. Muestra contexto (source fact) + pregunta + 4 opciones numeradas
4. Lee entrada: `1/2/3/4` o `s`
5. `svc.grade(quiz, index)` → muestra "Correct!" o "Incorrect. Correct: X"
6. Si `s` → `svc.skip(quiz)` → "Quiz skipped."

---

## `reviews list`

```python
@app.command("list")
def list_reviews() -> None:
    items = _service().get_pending()
    for item in items:
        typer.echo(f"  [{item.fact_topic}]  due: {item.next_review_date}  fails: {item.fail_count}  {item.fact_text[:50]}")
```

Muestra todos los items pendientes con su fecha de revisión, número de fallos y un extracto del fact.
