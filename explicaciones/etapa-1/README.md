# Etapa 1 — Setup + Storage base + Secrets scaffolding

Archivos implementados en esta etapa y sus explicaciones:

| Archivo en el proyecto | Explicación |
|---|---|
| `factpop/__main__.py` y `factpop/app/__main__.py` | [main.md](main.md) |
| `factpop/app/lifecycle.py` | [lifecycle.md](lifecycle.md) |
| `factpop/app/bootstrap.py` y `factpop/app/cli.py` | [bootstrap_y_cli.md](bootstrap_y_cli.md) |
| `factpop/shared/storage/tinydb_factory.py` | [tinydb_factory.md](tinydb_factory.md) |
| `factpop/shared/logging_config.py` | [logging_config.md](logging_config.md) |
| `factpop/shared/errors.py` | [errors.md](errors.md) |
| `requirements.txt`, `.gitignore`, `.env.example`, `pyrightconfig.json`, `.vscode/settings.json` | [config_proyecto.md](config_proyecto.md) |
| `scripts/bootstrap_dev.ps1` y `scripts/run_tests.ps1` | [scripts.md](scripts.md) |
| `tests/conftest.py`, `test_tinydb_factory.py`, `test_logging_config.py`, `test_errors.py` | [tests.md](tests.md) |

## Estructura de carpetas de Etapa 1

```
FactPop/
  factpop/
    __main__.py              ← entry point "python -m factpop"
    app/
      __main__.py            ← lógica de arranque del daemon
      lifecycle.py           ← lock de instancia única
      bootstrap.py           ← wiring de servicios (skeleton)
      cli.py                 ← CLI admin (skeleton)
    features/                ← módulos stub (se implementan en etapas 2-8)
      topics/ schedules/ facts/ notifications/
      history/ quizzes/ reviews/ settings/
    shared/
      storage/
        tinydb_factory.py    ← singleton TinyDB + init de tablas
      logging_config.py      ← setup de rotating file + console handlers
      errors.py              ← jerarquía base de excepciones
  tests/
    conftest.py              ← fixture autouse para resetear singleton DB
    integration/
      test_tinydb_factory.py ← 7 tests de integración con TinyDB real
    unit/shared/
      test_logging_config.py ← 5 tests unitarios con mock de user_log_dir
      test_errors.py         ← 2 tests de jerarquía de excepciones
  scripts/
    bootstrap_dev.ps1        ← setup del entorno (venv + deps + .env)
    run_tests.ps1            ← ejecutar pytest
  .gitignore                 ← excluye .env, .venv, __pycache__, etc.
  .env.example               ← plantilla de variables de entorno
  .env                       ← secretos reales (NO commiteado)
  requirements.txt           ← dependencias del proyecto
  pyrightconfig.json         ← config de Pyright para VS Code
  .vscode/settings.json      ← intérprete Python + config de tests
```
