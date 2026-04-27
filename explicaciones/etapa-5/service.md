# `factpop/features/history/service.py`

**Propósito:** Orquesta la persistencia de facts. Es el punto de entrada que usarán tanto el módulo de facts (Etapa 6) como el de quizzes (Etapa 8).

---

```python
def record(self, topic: str, text: str, example: str | None = None) -> FactRecord:
    fact = FactRecord(
        id=str(uuid.uuid4()),
        topic=topic,
        text=text,
        shown_at=datetime.now().isoformat(timespec="seconds"),
        example=example,
        saved=False,
    )
    self._repo.insert(fact)
    return fact
```

- `uuid.uuid4()` — ID único universal aleatorio
- `datetime.now().isoformat(timespec="seconds")` — timestamp actual en formato `"2026-04-25T10:00:00"`. `timespec="seconds"` omite microsegundos para mantener el string limpio
- `saved=False` — todos los facts empiezan como no guardados
- Retorna el `FactRecord` creado para que el llamador tenga el `id` (útil para `mark_saved` en el mismo flujo)

---

```python
def get_recent(self, topic: str | None = None, limit: int = 50) -> list[FactRecord]:
    return self._repo.list_recent(topic=topic, limit=limit)
```

API de consulta para otros módulos:
- **Etapa 6 (fact generation):** `get_recent(topic="Java", limit=10)` para verificar duplicados
- **Etapa 8 (quiz system):** `get_recent(limit=50)` para elegir un fact como base del quiz

---

## ¿Por qué el ID se genera en el service y no en el repo?

A diferencia del `TopicRepository` (Etapa 2), aquí el service genera el ID y lo pasa al repo. Esto es porque el service necesita devolver el `FactRecord` completo con su ID al llamador — si el repo lo generara internamente, tendría que devolverlo de alguna forma. Es más limpio que el service construya el objeto completo.
