# `factpop/features/topics/models.py`

**Propósito:** Define la estructura de datos que representa un tema de aprendizaje en la app. Es el objeto que viaja entre el repositorio, el servicio y el CLI.

---

```python
from __future__ import annotations
```
Habilita tipos modernos (`str | None`, etc.) en Python 3.9+.

```python
from dataclasses import dataclass, field
```
- `dataclass` — decorador que genera automáticamente `__init__`, `__repr__`, y `__eq__` basándose en los campos declarados.
- `field` — función para configurar campos con valores por defecto o comportamientos especiales.

---

```python
@dataclass
class Topic:
    id: str
    name: str
    active: bool = field(default=True)
```

**`@dataclass`** — en vez de escribir manualmente:
```python
def __init__(self, id, name, active=True):
    self.id = id
    self.name = name
    self.active = active
```
...el decorador lo genera automáticamente. También genera `__repr__` (`Topic(id='...', name='Java', active=True)`) y `__eq__` (dos topics son iguales si todos sus campos son iguales).

**`id: str`** — identificador único del tema. Se genera como UUID en el repositorio, nunca en el modelo.

**`name: str`** — nombre del tema tal como el usuario lo ingresó (ej: `"Spring Boot"`). Se preserva el case original.

**`active: bool = field(default=True)`** — si el tema está activo (elegible para selección aleatoria). `True` por defecto: todos los temas nuevos están activos.

`field(default=True)` es equivalente a `active: bool = True` en este caso. Se usa `field()` cuando se necesita configuración adicional (ej: `field(default_factory=list)` para campos mutables como listas).

---

## ¿Por qué un dataclass y no un dict?

TinyDB guarda dicts en JSON. El repositorio convierte entre dicts (TinyDB) y `Topic` (código Python). Esto ofrece:

| Dict `{"id": "...", "name": "Java"}` | `Topic(id="...", name="Java")` |
|---|---|
| `row["name"]` — puede lanzar `KeyError` | `topic.name` — type-safe, el IDE lo valida |
| No hay documentación de qué campos existen | Los campos están declarados explícitamente |
| Autocompletion del IDE no funciona | Autocompletion completo |
| Cualquier string como clave | Solo campos declarados en la clase |
