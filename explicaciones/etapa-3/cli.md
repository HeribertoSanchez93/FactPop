# `factpop/features/schedules/cli.py` y `factpop/features/settings/cli.py`

## `schedules/cli.py`

```python
app = typer.Typer(help="Manage popup schedule.")
random_app = typer.Typer(help="Manage random-interval mode.")
app.add_typer(random_app, name="random")
```

El módulo tiene **dos niveles de subcomandos**:
- `schedules add/remove/list` — directamente bajo `schedules`
- `schedules random enable/disable` — bajo el sub-Typer `random`

Esto produce la jerarquía:
```
factpop-cli schedules add 09:00
factpop-cli schedules remove 09:00
factpop-cli schedules list
factpop-cli schedules random enable [--start] [--end] [--max]
factpop-cli schedules random disable
```

---

```python
@random_app.command("enable")
def random_enable(
    start: str = typer.Option("08:00", help="Window start time (HH:MM)"),
    end: str = typer.Option("22:00", help="Window end time (HH:MM)"),
    max: int = typer.Option(3, help="Max popups per day"),
) -> None:
```

`typer.Option` (con doble guión `--`) en vez de `typer.Argument` (posicional) porque los parámetros son opcionales y tienen defaults. El usuario puede escribir solo `schedules random enable` y obtener la configuración por defecto.

---

## `settings/cli.py` — quiz toggle

```python
class QuizToggle(str, Enum):
    on = "on"
    off = "off"
```

Se usa un `Enum` para limitar los valores aceptados a exactamente `"on"` y `"off"`. Si el usuario escribe `quiz toggle maybe`, Typer rechaza el input automáticamente con un mensaje de uso — sin necesidad de código de validación manual.

```python
@app.command("toggle")
def toggle(state: QuizToggle = typer.Argument(..., help="'on' or 'off'")) -> None:
    enabled = state == QuizToggle.on
    _service().set_quiz_enabled(enabled)
    label = "enabled" if enabled else "disabled"
    typer.echo(f"OK: Quizzes {label}.")
```

`state == QuizToggle.on` devuelve `True` si el argumento fue `"on"`, `False` si fue `"off"`. Simple y sin `if/elif` innecesarios.

---

## Registro en `factpop/app/cli.py`

```python
app.add_typer(schedules_cli.app, name="schedules")
app.add_typer(settings_cli.app, name="quiz")
```

El CLI principal queda:
```
factpop-cli
  topics    add/list/activate/deactivate/delete
  schedules add/remove/list/random
  quiz      toggle
```
