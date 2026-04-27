# `factpop/features/settings/service.py`

**Propósito:** Proporciona acceso **tipado** a la configuración. El repositorio es genérico (`get(key)` devuelve `Any`); el servicio expone métodos con tipos concretos y valores por defecto semánticos.

---

```python
_KEY_SCHEDULE_TIMES = "schedule_times"
_KEY_QUIZ_ENABLED   = "quiz_enabled"
_KEY_RANDOM_ENABLED = "random_enabled"
_KEY_RANDOM_START   = "random_start"
_KEY_RANDOM_END     = "random_end"
_KEY_RANDOM_MAX     = "random_max_per_day"
```
Constantes para las claves del almacén. Centralizarlas evita typos dispersos en el código. Si se renombra una clave, se cambia en un solo lugar.

---

```python
def get_schedule_times(self) -> list[str]:
    return self._repo.get(_KEY_SCHEDULE_TIMES, default=[])
```
Devuelve la lista de horarios configurados. Si nunca se configuró, devuelve `[]` (no `None`), lo que simplifica el código que la usa: siempre es una lista iterable.

---

```python
def is_quiz_enabled(self) -> bool:
    return self._repo.get(_KEY_QUIZ_ENABLED, default=True)
```
Quizzes están habilitados **por defecto** (`default=True`). Un usuario nuevo no necesita configurar nada para que los quizzes funcionen.

---

```python
def get_random_config(self) -> RandomModeConfig:
    return RandomModeConfig(
        enabled=self._repo.get(_KEY_RANDOM_ENABLED, default=False),
        start=self._repo.get(_KEY_RANDOM_START, default="08:00"),
        end=self._repo.get(_KEY_RANDOM_END, default="22:00"),
        max_per_day=self._repo.get(_KEY_RANDOM_MAX, default=3),
    )
```
Construye un `RandomModeConfig` desde múltiples claves. Los defaults coinciden con los de la spec: ventana 08:00-22:00, máximo 3 popups por día, modo aleatorio deshabilitado.

```python
def set_random_config(self, config: RandomModeConfig) -> None:
    self._repo.set(_KEY_RANDOM_ENABLED, config.enabled)
    self._repo.set(_KEY_RANDOM_START, config.start)
    self._repo.set(_KEY_RANDOM_END, config.end)
    self._repo.set(_KEY_RANDOM_MAX, config.max_per_day)
```
Guarda los 4 campos de la configuración en claves separadas. Esto permite consultar individualmente cada campo sin deserializar un objeto completo.
