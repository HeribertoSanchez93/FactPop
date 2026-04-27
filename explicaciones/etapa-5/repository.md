# `factpop/features/history/repository.py`

**Propósito:** Persistencia de `FactRecord` en TinyDB con enforcement del cap máximo.

---

## Cap enforcement en `insert()`

```python
def insert(self, record: FactRecord) -> None:
    if self.count() >= self._max_size:
        self._evict_oldest_non_saved()
    self._table.insert(self._to_dict(record))
```

El cap se verifica **antes** de insertar. Si ya se alcanzó el máximo, se intenta evictar. Si no hay nada que evictar (todos son saved), se inserta de todos modos — los saved facts son inmunes.

```python
def _evict_oldest_non_saved(self) -> None:
    rows = [r for r in self._table.all() if not r["saved"]]
    if not rows:
        return  # todos saved — no evictar
    oldest = min(rows, key=lambda r: r["shown_at"])
    self._table.remove(cond=lambda row: row["id"] == oldest["id"])
```

- Filtra solo los registros con `saved=False`
- Encuentra el más antiguo comparando `shown_at` (string ISO 8601 — ordena correctamente)
- Elimina ese registro por `id`
- Si no hay no-saved: `return` sin hacer nada → el insert procede y excede el cap

---

## Ordenamiento en `list_recent()`

```python
def list_recent(self, topic: str | None = None, limit: int = 50) -> list[FactRecord]:
    rows = self._table.all()
    if topic is not None:
        rows = [r for r in rows if r["topic"] == topic]
    rows.sort(key=lambda r: r["shown_at"], reverse=True)
    return [self._to_model(r) for r in rows[:limit]]
```

`rows.sort(..., reverse=True)` ordena de más reciente a más antiguo. El `[:limit]` corta los primeros N resultados (que son los más recientes). Esto es lo que necesita tanto el CLI como el servicio de quizzes (Etapa 8) para obtener los facts más recientes.

---

## `_to_model()` y `_to_dict()`

Métodos estáticos que convierten entre el dict de TinyDB y el dataclass `FactRecord`. `row.get("example")` usa `.get()` (devuelve `None` si la clave no existe) para backward compatibility con registros que no tengan el campo.
