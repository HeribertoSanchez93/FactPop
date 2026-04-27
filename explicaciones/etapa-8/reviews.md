# Reviews — modelos, repositorio, interfaz y servicio

## `ReviewItem` model

```python
@dataclass
class ReviewItem:
    id: str
    fact_id: str
    fact_text: str      # guardado para poder generar un quiz sin consultar history
    fact_topic: str
    next_review_date: str   # ISO date "2026-04-26"
    fail_count: int = 1
    resolved: bool = False
```

`fact_text` y `fact_topic` se almacenan en el item para que el `QuizService` pueda construir el `FactRecord` directamente desde el review queue, sin necesitar hacer un lookup adicional al historial.

---

## `ReviewScheduler` Protocol

```python
class ReviewScheduler(Protocol):
    def enqueue(self, fact: FactRecord, as_of_date: str | None = None) -> None: ...
    def increment_fail(self, fact_id: str, as_of_date: str | None = None) -> None: ...
    def resolve(self, fact_id: str) -> None: ...
    def get_due(self, as_of_date: str | None = None) -> list[ReviewItem]: ...
    def get_pending(self) -> list[ReviewItem]: ...
```

`QuizService` depende de `ReviewScheduler` (protocolo), no de `ReviewService` (clase concreta). Cumple DIP: la lógica de negocio de quizzes no conoce detalles de implementación de la cola de revisión.

---

## `ReviewService.enqueue()` — lógica de backoff

```python
def enqueue(self, fact: FactRecord, as_of_date: str | None = None) -> None:
    existing = self._repo.find_by_fact_id(fact.id)
    if existing is not None and not existing.resolved:
        self.increment_fail(fact.id, as_of_date)
        return
    # ... insert new item con next_review_date = today + 1
```

Si el fact ya está en la queue (el usuario falló el mismo quiz antes), no crea un duplicado — llama `increment_fail()` para extender el plazo.

```python
def increment_fail(self, fact_id: str, as_of_date: str | None = None) -> None:
    item.fail_count += 1
    extra_days = min(item.fail_count, 7)   # cap: +7 días máximo
    item.next_review_date = today + extra_days days
    self._repo.update(item)
```

Con `fail_count` como número de fallos totales y cap en 7, la fecha nunca excede `today + 7`.

---

## `TinyDBReviewRepository.get_due()`

```python
def get_due(self, as_of_date: str) -> list[ReviewItem]:
    return [
        self._to_model(r)
        for r in self._table.all()
        if not r["resolved"] and r["next_review_date"] <= as_of_date
    ]
```

La comparación `next_review_date <= as_of_date` funciona con strings ISO 8601 (`"2026-04-25" <= "2026-04-26"` = `True`) porque ISO 8601 ordena lexicográficamente igual que por fecha. No se necesita conversión a `datetime`.
