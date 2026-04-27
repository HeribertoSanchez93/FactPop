# Tests de Etapa 1

## `tests/conftest.py` — Configuración global de pytest

```python
import pytest
import factpop.shared.storage.tinydb_factory as db_module
```
- `pytest` — framework de tests.
- Importa el módulo completo (no solo una función) para poder resetear su variable global `_db`.

```python
@pytest.fixture(autouse=True)
def reset_db_singleton():
    """Reset the TinyDB singleton before and after every test."""
    db_module.close_db()
    yield
    db_module.close_db()
```

**¿Qué es un fixture?**
Un fixture es código de setup/teardown que pytest ejecuta antes y/o después de los tests. Se define con `@pytest.fixture`.

- `autouse=True` — este fixture se aplica **automáticamente a todos los tests** sin necesidad de declararlo en cada función de test.
- `db_module.close_db()` (antes del yield) — resetea el singleton antes de cada test para que empiece con estado limpio.
- `yield` — aquí se ejecuta el test.
- `db_module.close_db()` (después del yield) — resetea el singleton después del test, liberando el archivo TinyDB.

**¿Por qué es necesario?**

`tinydb_factory.py` usa un singleton global (`_db`). Si un test lo inicializa con `tmp_path/test.json`, el siguiente test lo encontraría ya inicializado apuntando al archivo del test anterior. El fixture garantiza que cada test comienza con `_db = None`.

---

## `tests/integration/test_tinydb_factory.py`

**Tests de integración:** usan TinyDB real con archivos temporales (no mocks). Verifican el comportamiento real del módulo.

```python
from pathlib import Path
import pytest
import factpop.shared.storage.tinydb_factory as factory
from factpop.shared.storage.tinydb_factory import _TABLES
```
Imports necesarios. `_TABLES` se importa para verificar que todas las tablas esperadas sean accesibles.

---

```python
def test_init_db_creates_file(tmp_path: Path) -> None:
    db_path = tmp_path / "test.json"
    db = factory.init_db(path=db_path)

    assert db_path.exists(), "DB file must be created on disk"
    assert db is not None
```
- `tmp_path` — fixture de pytest que provee una carpeta temporal única por test (se borra al final).
- Verifica que `init_db()` crea el archivo JSON en disco.
- `assert db is not None` — verifica que se retornó un objeto TinyDB válido.

---

```python
def test_init_db_all_tables_accessible(tmp_path: Path) -> None:
    db = factory.init_db(path=tmp_path / "test.json")

    for table_name in _TABLES:
        table = db.table(table_name)
        assert table is not None, f"Table '{table_name}' must be accessible"
```
Verifica que las 5 tablas (`topics`, `app_config`, `fact_history`, `quiz_attempts`, `review_queue`) sean accesibles después de `init_db()`.

---

```python
def test_init_db_returns_same_singleton(tmp_path: Path) -> None:
    db1 = factory.init_db(path=tmp_path / "test.json")
    db2 = factory.init_db(path=tmp_path / "test.json")

    assert db1 is db2, "init_db must return the same TinyDB instance (singleton)"
```
- `is` verifica identidad de objeto (misma instancia en memoria), no solo igualdad de valor.
- Confirma que llamar `init_db()` dos veces no crea dos conexiones separadas.

---

```python
def test_close_db_resets_singleton(tmp_path: Path) -> None:
    db1 = factory.init_db(path=tmp_path / "first.json")
    factory.close_db()

    db2 = factory.init_db(path=tmp_path / "second.json")
    assert db1 is not db2, "After close_db, init_db must return a fresh instance"
```
Verifica que después de `close_db()`, la siguiente llamada a `init_db()` crea una instancia nueva (no reutiliza la cerrada).

---

```python
def test_close_db_idempotent() -> None:
    factory.close_db()
    factory.close_db()  # calling twice must not raise
```
Verifica que llamar `close_db()` dos veces seguidas no lanza ninguna excepción. "Idempotente" = el resultado es el mismo sin importar cuántas veces se llama.

---

```python
def test_tables_survive_reopen(tmp_path: Path) -> None:
    db_path = tmp_path / "test.json"

    db = factory.init_db(path=db_path)
    db.table("topics").insert({"name": "Java", "active": True})
    factory.close_db()

    db = factory.init_db(path=db_path)
    rows = db.table("topics").all()
    assert len(rows) == 1
    assert rows[0]["name"] == "Java"
```
El test más importante: verifica que los datos **persisten en disco** entre sesiones. Cierra la DB, la reabre, y confirma que el registro insertado sigue ahí.

---

## `tests/unit/shared/test_logging_config.py`

**Tests unitarios con mocks:** no escriben a la carpeta real de logs, usan `tmp_path` y `unittest.mock.patch`.

```python
from unittest.mock import patch
```
`patch` permite reemplazar temporalmente una función o variable por un mock. Aquí se usa para reemplazar `user_log_dir` con una función que devuelve `tmp_path` en vez de la carpeta real del SO.

```python
@pytest.fixture(autouse=True)
def reset_root_logger():
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    yield
    root.handlers = original_handlers
    root.setLevel(original_level)
```
Cada llamada a `setup_logging()` agrega handlers al logger raíz. Sin este fixture, los tests siguientes tendrían handlers duplicados. El fixture guarda el estado original y lo restaura después de cada test.

---

```python
def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "factpop.log"

    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    assert log_file.exists(), "Log file must be created on disk"
```
- `patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path))` — reemplaza `user_log_dir` dentro del módulo `logging_config` por una función que devuelve `str(tmp_path)`. Así el log se escribe en el directorio temporal del test, no en `%LOCALAPPDATA%`.
- Verifica que el archivo `factpop.log` fue creado en `tmp_path`.

---

```python
def test_log_message_written_to_file(tmp_path: Path) -> None:
    log_file = tmp_path / "factpop.log"

    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    logging.getLogger("factpop.test").info("stage1-sentinel")

    content = log_file.read_text(encoding="utf-8")
    assert "stage1-sentinel" in content
```
El test más completo: configura el logging, escribe un mensaje con un texto único ("stage1-sentinel"), lee el archivo de log, y verifica que el texto esté ahí. Confirma el flujo completo de principio a fin.

---

## `tests/unit/shared/test_errors.py`

```python
def test_factpop_error_is_exception() -> None:
    assert issubclass(FactPopError, Exception)
```
Verifica que `FactPopError` herede de `Exception` (la clase base de todos los errores en Python). Si no heredara de `Exception`, no podría ser capturada con `except FactPopError`.

```python
def test_factpop_error_can_be_raised_and_caught() -> None:
    with pytest.raises(FactPopError, match="boom"):
        raise FactPopError("boom")
```
- `pytest.raises(FactPopError, match="boom")` — context manager que verifica que el bloque `with` lanza `FactPopError` con un mensaje que contiene "boom".
- Si no se lanza la excepción, o se lanza otro tipo, el test falla.
