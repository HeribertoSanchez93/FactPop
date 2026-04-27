# Tests de Etapa 2 (TDD)

Los tests se escribieron **antes** de la implementación. Se corrieron primero y se confirmó que fallaban con `ModuleNotFoundError`. Solo después se escribió el código de producción.

---

## `tests/unit/features/test_topic_models.py` — 4 tests

Tests del dataclass `Topic`. Verifican que el modelo tenga la estructura correcta.

```python
def test_topic_is_active_by_default() -> None:
    topic = Topic(id="1", name="Java")
    assert topic.active is True
```
El campo `active` tiene `default=True`. Sin pasar `active`, debe ser `True`.

```python
def test_topic_can_be_created_inactive() -> None:
    topic = Topic(id="1", name="Java", active=False)
    assert topic.active is False
```
El campo `active` puede ser `False` explícitamente.

```python
def test_topic_name_is_preserved() -> None
def test_topic_id_is_preserved() -> None
```
Los campos se guardan tal cual se pasan — sin transformaciones.

---

## `tests/integration/test_topic_repository.py` — 17 tests

Usan **TinyDB con `MemoryStorage`** — un TinyDB que vive solo en RAM (más rápido que archivos, no deja estado en disco entre tests).

```python
@pytest.fixture
def repo() -> TinyDBTopicRepository:
    db = TinyDB(storage=MemoryStorage)
    return TinyDBTopicRepository(db.table("topics"))
```
Cada test recibe un repositorio fresco con una tabla vacía. El fixture `reset_db_singleton` de `conftest.py` no interfiere aquí porque este repo no usa el singleton global.

**Tests clave:**

```python
def test_find_by_name_is_case_insensitive(repo) -> None:
    repo.create("Java")
    assert repo.find_by_name("java") is not None
    assert repo.find_by_name("JAVA") is not None
    assert repo.find_by_name("jAvA") is not None
```
Verifica el requisito de la spec: duplicate check es case-insensitive.

```python
def test_save_persists_active_flag_change(repo) -> None:
    topic = repo.create("Java")
    topic.active = False
    repo.save(topic)
    found = repo.find_by_name("Java")
    assert found.active is False
```
Verifica que cambiar `topic.active` en Python y llamar `save()` realmente persiste el cambio en TinyDB.

```python
def test_tables_survive_reopen(repo) -> None:
```
No aplica en tests de repositorio de esta etapa (eso se testea en el repositorio de tinydb_factory).

```python
def test_delete_nonexistent_id_does_not_raise(repo) -> None:
    repo.delete("nonexistent-id")  # must not raise
```
El repositorio no debe lanzar error al eliminar un ID que no existe — esa verificación es responsabilidad del servicio.

---

## `tests/unit/features/test_topic_service.py` — 20 tests

Usan el mismo patrón `MemoryStorage` que los tests de repositorio. El servicio se construye con un repositorio real (no un mock), lo que da mayor confianza en el comportamiento integrado.

```python
@pytest.fixture
def service() -> TopicService:
    db = TinyDB(storage=MemoryStorage)
    repo = TinyDBTopicRepository(db.table("topics"))
    return TopicService(repo)
```

**Tests de validación:**

```python
def test_create_strips_leading_and_trailing_whitespace(service) -> None:
    topic = service.create("  Java  ")
    assert topic.name == "Java"
```
Verifica que el servicio limpia el nombre antes de guardarlo.

```python
def test_create_rejects_empty_name(service) -> None:
    with pytest.raises(EmptyTopicNameError):
        service.create("")

def test_create_rejects_whitespace_only_name(service) -> None:
    with pytest.raises(EmptyTopicNameError):
        service.create("   ")
```
Ambos deben lanzar la misma excepción — el whitespace solo queda vacío después del `strip()`.

**Test de deactivate con flag is_last:**

```python
def test_deactivate_returns_is_last_true_when_only_active_topic(service) -> None:
    service.create("Java")
    _, is_last = service.deactivate("Java")
    assert is_last is True

def test_deactivate_returns_is_last_false_when_other_active_topics_exist(service) -> None:
    service.create("Java")
    service.create("Python")
    _, is_last = service.deactivate("Java")
    assert is_last is False
```
El `_` descarta el primer elemento de la tupla (el topic). Solo importa el flag `is_last`.

---

## `tests/unit/features/test_topic_cli.py` — 13 tests

Usan **`typer.testing.CliRunner`** — un cliente de test para CLIs de Typer. Similar al `TestClient` de FastAPI.

```python
@pytest.fixture
def runner(tmp_path: Path) -> CliRunner:
    db_module.init_db(path=tmp_path / "test.json")
    return CliRunner()
```
El fixture:
1. Inicializa el singleton de TinyDB con un archivo temporal (no toca la BD real).
2. El `autouse=True` de `conftest.py` cierra el singleton antes y después de cada test.

```python
def test_cli_topics_add_creates_topic(runner: CliRunner) -> None:
    result = runner.invoke(app, ["topics", "add", "Java"])
    assert result.exit_code == 0
    assert "Java" in result.output
```
- `runner.invoke(app, [...])` — ejecuta el CLI con los argumentos dados en memoria (sin proceso real).
- `result.exit_code` — 0 = éxito, 1 = error.
- `result.output` — todo lo impreso en stdout.

```python
def test_cli_topics_add_duplicate_shows_error(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "add", "Java"])
    assert result.exit_code != 0
    assert "already exists" in result.output.lower() or "duplicate" in result.output.lower()
```
Llama `add Java` dos veces. El segundo debe fallar. El error va a stderr, pero el CliRunner lo mezcla en `result.output` por defecto.

```python
def test_cli_topics_deactivate_last_active_shows_warning(runner: CliRunner) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    result = runner.invoke(app, ["topics", "deactivate", "Java"])
    assert result.exit_code == 0
    assert "warning" in result.output.lower() or "no active" in result.output.lower()
```
Exit code es 0 (no es un error), pero el output debe contener el warning de "no active topics remain".

---

## ¿Por qué MemoryStorage en vez de mocks?

**Con mocks:**
```python
repo = Mock()
repo.find_by_name.return_value = None
repo.create.return_value = Topic(id="1", name="Java")
```
Problema: estás testeando que llamas los métodos del mock correctamente, no que el sistema funciona. Si hay un bug en el repositorio real, los tests con mocks no lo detectan.

**Con MemoryStorage:**
```python
db = TinyDB(storage=MemoryStorage)
repo = TinyDBTopicRepository(db.table("topics"))
```
Ventajas: el repositorio real corre, sin archivos en disco, sin limpiar nada. Los tests verifican la integración real entre servicio y repositorio.
