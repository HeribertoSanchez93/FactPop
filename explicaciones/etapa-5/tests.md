# Tests de Etapa 5 (TDD) — 36 tests nuevos

## Uso de `freezegun`

```python
from freezegun import freeze_time

@freeze_time("2026-04-25T10:00:00")
def test_record_returns_fact_record(service: FactHistoryService) -> None:
    r = service.record(topic="Java", text="Java uses JVM.")
    assert r.shown_at == "2026-04-25T10:00:00"
```

`@freeze_time("2026-04-25T10:00:00")` hace que `datetime.now()` devuelva siempre esa fecha durante el test. Sin esto, el timestamp del fact dependería de cuándo corra el test — no determinístico.

También se usa dentro de tests para simular distintos momentos:

```python
def test_get_recent_returns_most_recent_first(service) -> None:
    with freeze_time("2026-04-25T08:00:00"):
        service.record(topic="Java", text="oldest")
    with freeze_time("2026-04-25T10:00:00"):
        service.record(topic="Java", text="newest")
    with freeze_time("2026-04-25T09:00:00"):
        service.record(topic="Java", text="middle")

    results = service.get_recent()
    assert results[0].text == "newest"
    assert results[2].text == "oldest"
```

Los facts se insertan en orden "no cronológico" (`oldest`, `newest`, `middle`) para verificar que el repositorio ordena correctamente por `shown_at`, no por orden de inserción.

---

## Tests del cap (los más importantes)

```python
def test_insert_evicts_oldest_non_saved_when_at_cap(small_repo) -> None:
    # Inserta 3 records (igual al cap)
    r1 = _make_record(text="oldest", shown_at="2026-04-25T08:00:00")
    r2 = _make_record(text="middle", shown_at="2026-04-25T09:00:00")
    r3 = _make_record(text="newest-before-cap", shown_at="2026-04-25T10:00:00")
    # ...inserta los 3...

    r4 = _make_record(text="triggers-eviction", shown_at="2026-04-25T11:00:00")
    small_repo.insert(r4)

    assert small_repo.count() == 3     # cap respetado
    assert small_repo.find_by_id(r1.id) is None  # r1 (más antiguo) eliminado
    assert small_repo.find_by_id(r4.id) is not None  # r4 guardado
```

```python
def test_insert_does_not_evict_saved_records(small_repo) -> None:
    # Marca todos como saved
    for r in (r1, r2, r3):
        small_repo.insert(r)
        small_repo.mark_saved(r.id)

    small_repo.insert(r4)

    assert small_repo.count() == 4  # cap excedido — saved son inmunes
    assert small_repo.find_by_id(r1.id) is not None  # saved, nunca eliminado
```

```python
def test_insert_evicts_oldest_non_saved_skipping_saved(small_repo) -> None:
    small_repo.insert(r1)
    small_repo.mark_saved(r1.id)  # r1 saved pero es el más antiguo
    small_repo.insert(r2)         # r2 no saved, segundo más antiguo
    small_repo.insert(r3)         # r3 no saved

    small_repo.insert(r4)  # triggers eviction

    assert small_repo.find_by_id(r1.id) is not None  # saved — protegido
    assert small_repo.find_by_id(r2.id) is None       # oldest NON-saved evicted
```

Estos tres tests juntos prueban los tres escenarios del spec:
1. Evicción normal del más antiguo no-saved
2. Cap excedido porque todos son saved (ninguno se elimina)
3. El más antiguo saved se salta, evicta el más antiguo no-saved

---

## `test_fact_history_cli.py` — Patrón helper

```python
def _add_fact(tmp_path: Path, topic: str, text: str, saved: bool = False) -> None:
    db = db_module.get_db()
    repo = TinyDBFactHistoryRepository(db.table("fact_history"))
    svc = FactHistoryService(repo)
    r = svc.record(topic=topic, text=text)
    if saved:
        svc.mark_saved(r.id)
```

Los tests del CLI no pueden llamar `_service()` directamente (es una función interna del `cli.py`). En su lugar, usan este helper que inserta facts directamente en la DB del test. El CLI luego los lee — verifica el comportamiento observable desde fuera.
