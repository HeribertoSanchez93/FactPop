# `factpop/features/topics/cli.py`

**Propósito:** Expone las operaciones del servicio de topics como comandos de terminal. Es la interfaz entre el usuario y la lógica de negocio durante las etapas de desarrollo y verificación.

**Responsabilidad única:** presentar inputs del usuario al servicio, y presentar el resultado (o error) al usuario. No contiene lógica de negocio.

---

```python
import typer
from factpop.features.topics.errors import (...)
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.storage.tinydb_factory import get_db
```
Importa Typer para el CLI, los errores para manejarlos, y la cadena de dependencias para construir el servicio.

```python
app = typer.Typer(help="Manage learning topics.")
```
Crea la sub-aplicación CLI del módulo de topics. Este `app` se registra en el CLI principal con `app.add_typer(topics_cli.app, name="topics")`.

---

```python
def _service() -> TopicService:
    db = get_db()
    return TopicService(TinyDBTopicRepository(db.table("topics")))
```
**Factory function** que construye el `TopicService` con sus dependencias reales cada vez que se llama un comando. 

- `get_db()` — devuelve el singleton TinyDB (ya inicializado en `__main__.py`).
- `db.table("topics")` — obtiene la tabla de topics.
- `TinyDBTopicRepository(tabla)` → `TopicService(repo)` — construye la cadena de dependencias.

El guión bajo `_service` indica que es una función interna del módulo (no parte de la API pública).

---

### Comando `add`

```python
@app.command("add")
def add(name: str = typer.Argument(..., help="Topic name")) -> None:
    """Add a new learning topic."""
    try:
        topic = _service().create(name)
        typer.echo(f"OK: Topic '{topic.name}' added (active).")
    except EmptyTopicNameError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    except DuplicateTopicError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
```

- `@app.command("add")` — registra la función como el subcomando `topics add`.
- `typer.Argument(..., help=...)` — el `...` indica que el argumento es **obligatorio**. Sin él, Typer muestra un error de uso.
- `typer.echo(...)` — imprime en stdout. En tests con `CliRunner`, se captura en `result.output`.
- `typer.echo(..., err=True)` — imprime en **stderr**. Convención: errores van a stderr, output normal a stdout.
- `raise typer.Exit(code=1)` — termina el proceso con código de salida 1 (error). Typer necesita que se use `typer.Exit` en vez de `sys.exit` para que funcione correctamente con el `CliRunner` de tests.

---

### Comando `list`

```python
@app.command("list")
def list_topics() -> None:
    """List all learning topics."""
    topics = _service().list_all()
    if not topics:
        typer.echo("No topics yet. Add one with: factpop-cli topics add <name>")
        return
    for topic in topics:
        status = "active" if topic.active else "inactive"
        typer.echo(f"  [{status}]  {topic.name}")
```
- Nombre interno `list_topics` (no `list` como el comando) para evitar colisión con el builtin `list` de Python.
- Si no hay topics: muestra un hint en vez de lista vacía (spec: "SHALL display an empty list with a hint").
- Formato `[active]  Java` — fácil de leer con el status al inicio.

---

### Comandos `activate` y `deactivate`

```python
@app.command("activate")
def activate(name: str = ...) -> None:
    try:
        topic = _service().activate(name)
        typer.echo(f"OK: Topic '{topic.name}' is now active.")
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
```

```python
@app.command("deactivate")
def deactivate(name: str = ...) -> None:
    try:
        topic, is_last = _service().deactivate(name)
        typer.echo(f"OK: Topic '{topic.name}' is now inactive.")
        if is_last:
            typer.echo(
                "Warning: no active topics remain. "
                "Popups will not fire until at least one topic is active."
            )
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
```

`deactivate` desempaqueta la tupla `(topic, is_last)` que devuelve el servicio. Si `is_last` es `True`, imprime el warning. El comando **exitcode siempre es 0** aunque sea el último activo — la spec dice que la desactivación puede proceder, solo hay que advertir.

---

### Comando `delete`

```python
@app.command("delete")
def delete(name: str = ...) -> None:
    try:
        _service().delete(name)
        typer.echo(f"OK: Topic '{name}' deleted.")
    except TopicNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
```
Elimina el topic o falla con exit code 1 si no existe.

---

## Registro en el CLI principal (`factpop/app/cli.py`)

```python
from factpop.features.topics import cli as topics_cli

app.add_typer(topics_cli.app, name="topics")
```

`add_typer` agrega el subgrupo `topics` al CLI principal. Resultado:

```
factpop-cli
  topics
    add <name>
    list
    activate <name>
    deactivate <name>
    delete <name>
```

Cada etapa futura agrega su propio grupo al CLI de la misma forma.
