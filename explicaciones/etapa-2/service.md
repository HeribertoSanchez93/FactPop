# `factpop/features/topics/service.py`

**Propósito:** Contiene las **reglas de negocio** del módulo de topics. Es la capa que decide qué está permitido y qué no — el repositorio solo guarda y lee datos, el servicio decide cuándo y con qué condiciones.

**Principio aplicado:** Single Responsibility — el servicio no habla con TinyDB directamente (eso es el repositorio), ni maneja la presentación al usuario (eso es el CLI).

---

```python
from factpop.features.topics.errors import (
    DuplicateTopicError, EmptyTopicNameError, TopicNotFoundError,
)
from factpop.features.topics.models import Topic
from factpop.features.topics.repository import TinyDBTopicRepository
```
Importa solo lo que necesita del módulo de topics.

---

```python
class TopicService:
    def __init__(self, repo: TinyDBTopicRepository) -> None:
        self._repo = repo
```
**Dependency Injection:** el servicio recibe el repositorio por constructor, no lo crea internamente. Beneficios:
- En **tests**, se inyecta un repositorio con `MemoryStorage` (sin archivos).
- En **producción**, se inyecta el repositorio con el TinyDB real.
- El servicio no sabe ni le importa cómo se persisten los datos.

---

### `create(name: str) -> Topic`

```python
def create(self, name: str) -> Topic:
    name = name.strip()
    if not name:
        raise EmptyTopicNameError("Topic name must not be empty.")
    if self._repo.find_by_name(name) is not None:
        raise DuplicateTopicError(f"Topic '{name}' already exists.")
    return self._repo.create(name)
```

**Reglas de negocio aplicadas en orden:**

1. `name.strip()` — elimina espacios del inicio y fin. `"  Java  "` se convierte en `"Java"`. El nombre guardado es el limpio.
2. `if not name` — después del strip, si el string está vacío (`""`) o era solo espacios (`"   "`), lanza `EmptyTopicNameError`.
3. `self._repo.find_by_name(name)` — busca case-insensitive. Si existe algún topic con ese nombre, lanza `DuplicateTopicError`.
4. Solo si pasa ambas validaciones → delega al repositorio.

**Orden importa:** primero validar el nombre (sin hacer queries), luego verificar duplicado (una query).

---

### `list_all() -> list[Topic]`

```python
def list_all(self) -> list[Topic]:
    return self._repo.list_all()
```
Sin lógica adicional — el servicio delega directamente. Si en el futuro se añade ordenamiento o paginación, se hace aquí sin tocar el repositorio.

---

### `list_active() -> list[Topic]`

```python
def list_active(self) -> list[Topic]:
    return self._repo.list_active()
```
Devuelve solo topics activos. Será usado por el módulo de facts (Etapa 5) para seleccionar un tema aleatorio.

---

### `activate(name: str) -> Topic`

```python
def activate(self, name: str) -> Topic:
    topic = self._repo.find_by_name(name)
    if topic is None:
        raise TopicNotFoundError(f"Topic '{name}' not found.")
    topic.active = True
    self._repo.save(topic)
    return topic
```
1. Busca el topic por nombre (case-insensitive).
2. Si no existe → lanza `TopicNotFoundError`.
3. Cambia el flag `active = True` en el objeto Python.
4. Persiste el cambio con `save()`.
5. Devuelve el topic actualizado.

---

### `deactivate(name: str) -> tuple[Topic, bool]`

```python
def deactivate(self, name: str) -> tuple[Topic, bool]:
    topic = self._repo.find_by_name(name)
    if topic is None:
        raise TopicNotFoundError(f"Topic '{name}' not found.")
    topic.active = False
    self._repo.save(topic)
    is_last = len(self._repo.list_active()) == 0
    return topic, is_last
```

**Retorna una tupla `(Topic, bool)`** donde el segundo valor indica si ya no quedan topics activos.

- `topic.active = False` + `save()` — persiste la desactivación.
- `len(self._repo.list_active()) == 0` — **después** de desactivar, cuenta cuántos activos quedan. Si es cero, `is_last = True`.
- Retorna ambos valores para que el CLI pueda mostrar el warning si corresponde.

**¿Por qué no bloquear la desactivación del último topic?** La spec dice "the deactivation MAY proceed but the system SHALL suppress popup generation while no active topics exist". El servicio desactiva y avisa; el scheduler verificará en etapas futuras.

---

### `delete(name: str) -> None`

```python
def delete(self, name: str) -> None:
    topic = self._repo.find_by_name(name)
    if topic is None:
        raise TopicNotFoundError(f"Topic '{name}' not found.")
    self._repo.delete(topic.id)
```
1. Busca el topic (la búsqueda es case-insensitive).
2. Si no existe → `TopicNotFoundError`.
3. Elimina por `id` (no por nombre) — los IDs son únicos, los nombres podrían tener edge cases.

**La spec dice:** "Deleting a topic SHALL NOT delete associated fact history." El servicio solo elimina el topic — la historia en `fact_history` mantiene el `topic_name` como string, no como foreign key.
