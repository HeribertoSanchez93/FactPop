# `factpop/app/bootstrap.py` y `factpop/app/cli.py`

---

## `factpop/app/bootstrap.py` — Capa de wiring (conexión de servicios)

```python
# Wiring layer: constructs and connects all services.
# Each stage will add its own service registrations here.
from __future__ import annotations


def bootstrap() -> None:
    """Initialize all application services. Called once at startup."""
    # Stage 1: storage and logging are initialized in __main__ before this.
    # Future stages will register repositories, services, and the scheduler here.
```

**¿Qué es el "wiring"?**

En arquitectura modular, ningún módulo debe crear sus propias dependencias. En vez de eso, existe un único lugar — `bootstrap.py` — que:
1. Crea todos los objetos (repositorios, servicios, scheduler, etc.)
2. Los inyecta donde los necesiten (Dependency Injection)

**En Etapa 1 está vacío** porque todavía no hay servicios que conectar. En etapas futuras, aquí irá código como:

```python
# (ejemplo futuro, no implementado aún)
def bootstrap() -> None:
    db = get_db()
    topic_repo = TopicRepository(db)
    topic_service = TopicService(topic_repo)
    fact_service = FactService(topic_repo, llm_client, history_repo)
    scheduler = ScheduleRunner(fact_service, ...)
    scheduler.start()
```

**¿Por qué separar esto de `__main__.py`?**

- `__main__.py` se encarga del *ciclo de vida del proceso* (arrancar, esperar, cerrar).
- `bootstrap.py` se encarga de *construir el grafo de objetos* de la app.
- Separar las dos responsabilidades (SRP — Single Responsibility Principle) facilita testear la lógica de wiring de forma independiente.

---

## `factpop/app/cli.py` — Entrada del comando `factpop-cli`

```python
from __future__ import annotations

import typer

app = typer.Typer(name="factpop-cli", help="FactPop admin CLI")


def main() -> None:
    app()
```

**¿Para qué sirve?**

El CLI es la herramienta de administración sin interfaz gráfica. Sirve para:
- Verificar cada etapa sin necesitar el tray icon ni popups.
- Ejecutar comandos como `factpop-cli topics add Java` desde la terminal.
- Automatizar operaciones en scripts.

**En Etapa 1 solo es un esqueleto.** Cada etapa futura le agrega subcomandos:
- Etapa 2 → `factpop-cli topics add/list/activate/delete`
- Etapa 3 → `factpop-cli schedules add/random`
- Etapa 4 → `factpop-cli llm ping`
- etc.

**¿Qué es Typer?**

Typer es una librería que convierte funciones Python en comandos CLI con argumentos tipados y `--help` automático. Ejemplo de cómo se verá en etapas futuras:

```python
# (ejemplo futuro)
@app.command()
def add(name: str = typer.Argument(..., help="Topic name")):
    """Add a new learning topic."""
    topic_service.create(name)
    typer.echo(f"Topic '{name}' added.")
```

**`app = typer.Typer(...)`** — crea la aplicación CLI. `name` es el nombre que aparece en `--help`. `help` es la descripción.

**`def main() -> None: app()`** — cuando se ejecuta `factpop-cli`, se llama `main()` que a su vez llama `app()`, que parsea los argumentos y ejecuta el subcomando correspondiente.
