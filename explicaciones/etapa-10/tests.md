# Tests de Etapa 10 (TDD) — 17 tests nuevos

## `test_auto_start.py` — 9 tests

Tests de la lógica pura de `auto_start.py` usando `unittest.mock.patch` para interceptar `_startup_folder()` y devolver un directorio temporal del test.

```python
def test_auto_start_configured_when_script_exists(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        script = get_startup_script_path()
        script.write_text("dummy content")
        assert is_auto_start_configured() is True
```

El patrón `patch("...._startup_folder", return_value=tmp_path)` es la única excepción al "no mocks" de TDD — se justifica porque la carpeta Startup real no existe en el entorno de test y no debe modificarse durante CI.

**Tests de contenido VBS:**
```python
def test_script_content_runs_hidden_no_console_window() -> None:
    content = build_startup_script_content(python_exe, project_dir)
    assert "0" in content or "hidden" in content.lower() or "vbHide" in content
```
Verifica que el VBS use `WindowStyle = 0` para no mostrar consola. Sin este test, un error de typo en el script causaría que FactPop abra una ventana negra molesta al arrancar Windows.

---

## `test_cli_status.py` — 8 tests

```python
def test_status_shows_correct_active_topic_count(runner: CliRunner) -> None:
    _seed_topics(runner, ["Java", "Python", "Kafka"])
    result = runner.invoke(app, ["status"])
    assert "3" in result.output

def test_status_shows_quiz_enabled_state(runner: CliRunner) -> None:
    runner.invoke(app, ["quiz", "toggle", "off"])
    result = runner.invoke(app, ["status"])
    assert "quiz" in result.output.lower()
    assert "disabled" in result.output.lower() or "off" in result.output.lower()
```

Los tests del status command también sirven como **tests de integración**: prueban que los servicios de topics, settings, history y reviews están correctamente conectados entre sí a través del CLI.

---

## Refactor: `app.command("status")(status_command)`

Durante el GREEN se descubrió que `app.add_typer(status_cli.app, name="status")` creaba una ruta `factpop-cli status status` (un subgrupo con un comando del mismo nombre). La solución fue registrar `status_command` directamente como comando top-level usando la API de decoradores de Typer de forma programática.

Este es el patrón correcto para comandos top-level que no forman un grupo:
```python
# En vez de add_typer:
app.command("status")(status_command)
# Equivale a decorar con:
# @app.command("status")
# def status_command(): ...
```
