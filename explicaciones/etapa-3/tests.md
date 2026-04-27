# Tests de Etapa 3 (TDD) — 56 tests nuevos

## `tests/integration/test_settings_repository.py` — 9 tests

Usan TinyDB con `MemoryStorage`. Prueban el repositorio key-value con diferentes tipos de valor.

```python
def test_get_returns_none_when_key_not_found(repo) -> None:
    assert repo.get("nonexistent") is None
```
El repositorio no lanza excepción para claves inexistentes — devuelve `None` (o el default).

```python
def test_set_overwrites_existing_value(repo) -> None:
    repo.set("quiz_enabled", True)
    repo.set("quiz_enabled", False)
    assert repo.get("quiz_enabled") is False
```
Verifica que `set()` hace upsert — no crea duplicados.

---

## `tests/unit/features/test_settings_service.py` — 9 tests

Verifican el acceso tipado con valores por defecto correctos.

```python
def test_quiz_is_enabled_by_default(service) -> None:
    assert service.is_quiz_enabled() is True
```
Sin configurar nada, quizzes están habilitados (default=True).

```python
def test_get_random_config_returns_defaults(service) -> None:
    config = service.get_random_config()
    assert config.enabled is False
    assert config.start == "08:00"
    assert config.end == "22:00"
    assert config.max_per_day == 3
```
Verifica que todos los defaults del `RandomModeConfig` coinciden con la spec.

---

## `tests/unit/features/test_schedule_service.py` — 22 tests

### Tests de validación de tiempo (8 tests)

```python
def test_add_time_rejects_hour_over_23(service) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("24:00")

def test_add_time_rejects_missing_leading_zero(service) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("9:00")

def test_add_time_rejects_wrong_separator(service) -> None:
    with pytest.raises(InvalidTimeFormatError):
        service.add_time("09-00")
```
Cubren todos los casos de formato inválido: hora fuera de rango, minutos fuera de rango, sin cero inicial, separador incorrecto, letras, string vacío.

### Tests de lógica de negocio

```python
def test_add_duplicate_time_raises_error(service) -> None:
    service.add_time("09:00")
    with pytest.raises(TimeAlreadyExistsError):
        service.add_time("09:00")
```

```python
def test_disable_random_preserves_window_settings(service) -> None:
    service.enable_random(start="09:00", end="21:00", max_per_day=5)
    service.disable_random()
    config = service.get_random_config()
    assert config.start == "09:00"  # preserved
    assert config.end == "21:00"    # preserved
    assert config.max_per_day == 5  # preserved
```
Verifica que desactivar el modo aleatorio NO borra los parámetros de ventana.

---

## `tests/unit/features/test_schedule_cli.py` — 16 tests

```python
def test_cli_schedules_random_enable_uses_defaults(runner) -> None:
    result = runner.invoke(app, ["schedules", "random", "enable"])
    assert result.exit_code == 0
    assert "08:00" in result.output
    assert "22:00" in result.output
```
El comando `random enable` sin argumentos usa los defaults y los muestra en el output.

```python
def test_cli_quiz_toggle_invalid_value(runner) -> None:
    result = runner.invoke(app, ["quiz", "toggle", "maybe"])
    assert result.exit_code != 0
```
Typer rechaza automáticamente valores fuera del Enum `QuizToggle` — el test verifica que el rechazo ocurre con exit code != 0.

---

## Refactor aplicado

Durante el GREEN, dos tests fallaron porque los mensajes de error no coincidían:
- `"25:00 is out of range"` no contenía "invalid" ni "format" → se cambió a `"Invalid time '25:00'..."`
- `"is not in the schedule"` no contenía "not found" → se cambió a `"not found in schedule"`

Esto siguió la regla TDD: **fix code, not tests**. Los tests definen el contrato de mensajes de error; el código debe adaptarse.
