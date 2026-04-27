# `factpop/features/topics/repository.py`

**Propósito:** Encapsula toda la interacción con TinyDB para el módulo de topics. El servicio y el CLI nunca llaman a TinyDB directamente — solo usan este repositorio.

**Patrón:** Repository — aísla la persistencia del resto del código. Si mañana se cambia TinyDB por SQLite o una API REST, solo se reemplaza este archivo.

---

```python
from __future__ import annotations
import uuid
from tinydb.table import Table
from factpop.features.topics.models import Topic
```
- `uuid` — módulo estándar de Python para generar identificadores únicos universales.
- `Table` — tipo de la tabla de TinyDB (no el DB completo, solo una tabla).
- `Topic` — el modelo de dominio al que se convierten los registros de TinyDB.

---

```python
class TinyDBTopicRepository:
    def __init__(self, table: Table) -> None:
        self._table = table
```
El constructor recibe una `Table` de TinyDB (no el `TinyDB` completo). Esto permite:
1. **Testear con `MemoryStorage`** — se puede crear una tabla en memoria sin archivos.
2. **Bajo acoplamiento** — el repositorio no sabe si la tabla viene de un archivo o de memoria.
3. **Consistencia** — múltiples repositorios (topics, history, quizzes) usan tablas separadas del mismo DB.

El `_` al inicio de `_table` indica que es un atributo privado — nadie fuera de la clase debe acceder a él.

---

```python
def create(self, name: str) -> Topic:
    topic_id = str(uuid.uuid4())
    self._table.insert({"id": topic_id, "name": name, "active": True})
    return Topic(id=topic_id, name=name, active=True)
```
- `uuid.uuid4()` — genera un UUID v4 (aleatorio). Ej: `"550e8400-e29b-41d4-a716-446655440000"`. `str(...)` lo convierte a string para guardarlo en JSON.
- `self._table.insert({...})` — inserta un documento JSON en TinyDB.
- `return Topic(...)` — convierte el dict insertado al dataclass Topic y lo devuelve al llamador.

**¿Por qué generar el ID en el repositorio y no en el servicio?** El repositorio es el que conoce el mecanismo de persistencia. En TinyDB, TinyDB mismo puede generar IDs (`doc_id`), pero usamos UUIDs propios para tener IDs estables independientemente de TinyDB.

---

```python
def find_by_name(self, name: str) -> Topic | None:
    needle = name.lower()
    for row in self._table.all():
        if row["name"].lower() == needle:
            return self._to_model(row)
    return None
```
- `name.lower()` — convierte el nombre buscado a minúsculas para comparación case-insensitive.
- `self._table.all()` — devuelve todos los documentos de la tabla como lista de dicts.
- `row["name"].lower() == needle` — compara en minúsculas. Así "Java", "java" y "JAVA" coinciden.
- Si no se encuentra: devuelve `None` (no lanza excepción — esa es responsabilidad del servicio).

**¿Por qué iterar en vez de usar `Query()`?** Para comparación case-insensitive, TinyDB necesita `.test(lambda ...)`. Iterar manualmente es igualmente legible y eficiente para el volumen esperado (<100 topics).

---

```python
def find_by_id(self, topic_id: str) -> Topic | None:
    for row in self._table.all():
        if row["id"] == topic_id:
            return self._to_model(row)
    return None
```
Búsqueda por ID exacto (sin case-insensitive porque los UUIDs son siempre lowercase).

---

```python
def list_all(self) -> list[Topic]:
    return [self._to_model(row) for row in self._table.all()]
```
List comprehension: itera todos los documentos, convierte cada uno a `Topic`, devuelve la lista. Devuelve lista vacía si no hay documentos.

```python
def list_active(self) -> list[Topic]:
    return [self._to_model(row) for row in self._table.all() if row["active"]]
```
Igual que `list_all` pero filtra solo los que tienen `active=True`. Usado por el scheduler para elegir temas aleatorios (etapas futuras).

---

```python
def save(self, topic: Topic) -> None:
    self._table.update(
        {"name": topic.name, "active": topic.active},
        cond=lambda row: row["id"] == topic.id,
    )
```
- `self._table.update(data, cond)` — actualiza los documentos que cumplan `cond` con los valores en `data`.
- `cond=lambda row: row["id"] == topic.id` — condición: solo el documento cuyo `id` coincide con el del topic.
- Solo actualiza `name` y `active` (no `id` — el ID nunca cambia).

---

```python
def delete(self, topic_id: str) -> None:
    self._table.remove(cond=lambda row: row["id"] == topic_id)
```
- `self._table.remove(cond)` — elimina todos los documentos que cumplan la condición.
- No lanza error si no existe — TinyDB simplemente no elimina nada. Es el servicio quien verifica si el topic existe antes de llamar `delete`.

---

```python
@staticmethod
def _to_model(row: dict) -> Topic:
    return Topic(id=row["id"], name=row["name"], active=row["active"])
```
- `@staticmethod` — método que no necesita `self` (no accede al estado de la instancia). Es una función auxiliar del repositorio.
- Convierte un dict de TinyDB `{"id": "...", "name": "Java", "active": True}` en un objeto `Topic`.
- Centralizar la conversión en un método evita repetir `Topic(id=row["id"], ...)` en cada método.
