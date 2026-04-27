# Etapa 2 — Topic Management

Archivos implementados en esta etapa:

| Archivo | Explicación |
|---|---|
| `factpop/features/topics/errors.py` | [errors.md](errors.md) |
| `factpop/features/topics/models.py` | [models.md](models.md) |
| `factpop/features/topics/repository.py` | [repository.md](repository.md) |
| `factpop/features/topics/service.py` | [service.md](service.md) |
| `factpop/features/topics/cli.py` | [cli.md](cli.md) |
| `tests/unit/features/test_topic_models.py` | [tests.md](tests.md) |
| `tests/integration/test_topic_repository.py` | [tests.md](tests.md) |
| `tests/unit/features/test_topic_service.py` | [tests.md](tests.md) |
| `tests/unit/features/test_topic_cli.py` | [tests.md](tests.md) |

## Estructura agregada en Etapa 2

```
factpop/features/topics/
  __init__.py    (stub de Etapa 1)
  errors.py      ← excepciones de dominio: Empty, Duplicate, NotFound
  models.py      ← dataclass Topic (id, name, active)
  repository.py  ← TinyDBTopicRepository (CRUD sobre TinyDB)
  service.py     ← TopicService (reglas de negocio)
  cli.py         ← comandos: add / list / activate / deactivate / delete

tests/unit/features/
  test_topic_models.py   ← 4 tests de modelo
  test_topic_service.py  ← 20 tests de servicio (con TinyDB in-memory)

tests/integration/
  test_topic_repository.py  ← 17 tests de repositorio (con TinyDB in-memory)

tests/unit/features/
  test_topic_cli.py  ← 13 tests de CLI (con CliRunner de Typer)
```

## Metodología TDD aplicada

Orden estricto RED → GREEN → REFACTOR:

1. **RED** — se escribieron todos los tests antes de crear cualquier archivo de implementación. Se corrió pytest y se confirmó que fallaban por `ModuleNotFoundError`.
2. **GREEN** — se implementó cada módulo en orden de dependencia: `errors` → `models` → `repository` → `service` → `cli`. Después de cada módulo se corrió pytest para verificar que los tests de ese módulo pasaran.
3. **REFACTOR** — se reemplazaron caracteres Unicode (`✓`) por ASCII puro al descubrir incompatibilidad con la codificación `cp1252` del terminal Windows.

## Gate de aceptación (todos pasan)

| Check | Resultado |
|---|---|
| `topics add Java` | `OK: Topic 'Java' added (active).` |
| `topics add java` (duplicate) | `Error: Topic 'java' already exists.` + exit 1 |
| `topics list` | muestra `[active]  Java` |
| `topics deactivate Java` (único activo) | deactiva + `Warning: no active topics remain.` |
| `topics delete Java` | `OK: Topic 'Java' deleted.` |
| `topics delete NonExistent` | `Error: Topic 'NonExistent' not found.` + exit 1 |
| `topics list` (vacío) | `No topics yet. Add one with: ...` |
| 68 tests pytest | todos pasan |
