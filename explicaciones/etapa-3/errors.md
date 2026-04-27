# `factpop/features/schedules/errors.py` y `factpop/features/schedules/models.py`

## errors.py

```python
class InvalidTimeFormatError(FactPopError):
    """Raised when a time string is not valid HH:MM (24-hour, 00:00–23:59)."""

class TimeAlreadyExistsError(FactPopError):
    """Raised when the exact time is already in the configured schedule."""

class TimeNotFoundError(FactPopError):
    """Raised when a time to remove is not in the configured schedule."""
```

Tres errores de dominio para el módulo de horarios:
- `InvalidTimeFormatError` — se lanza en validación (formato incorrecto o fuera de rango).
- `TimeAlreadyExistsError` — se lanza al agregar un tiempo ya existente.
- `TimeNotFoundError` — se lanza al intentar eliminar un tiempo que no está en la lista.

---

## models.py — `RandomModeConfig`

```python
@dataclass
class RandomModeConfig:
    enabled: bool = field(default=False)
    start: str = field(default="08:00")
    end: str = field(default="22:00")
    max_per_day: int = field(default=3)
```

Representa la configuración del modo aleatorio. Todos los campos tienen defaults para que se pueda crear con `RandomModeConfig()` y obtener una configuración sensata sin pasar argumentos.

| Campo | Tipo | Default | Significado |
|---|---|---|---|
| `enabled` | bool | False | Si el modo aleatorio está activo |
| `start` | str (HH:MM) | "08:00" | Inicio de la ventana diaria |
| `end` | str (HH:MM) | "22:00" | Fin de la ventana diaria |
| `max_per_day` | int | 3 | Máximo de popups aleatorios por día |
