# `factpop/features/settings/repository.py`

**Propósito:** Almacena configuración de la app como pares clave-valor en TinyDB. Es la única pieza que habla con la tabla `app_config`.

---

```python
class TinyDBSettingsRepository:
    def __init__(self, table: Table) -> None:
        self._table = table
```
Recibe la tabla `app_config` por constructor (DI). No sabe si es real o en memoria.

---

```python
def get(self, key: str, default: Any = None) -> Any:
    for row in self._table.all():
        if row["key"] == key:
            return row["value"]
    return default
```
Busca el documento con `key` coincidente y devuelve su `value`. Si no existe, devuelve `default` (que por defecto es `None`). Esto permite escribir `repo.get("quiz_enabled", default=True)` para valores con fallback.

---

```python
def set(self, key: str, value: Any) -> None:
    exists = any(row["key"] == key for row in self._table.all())
    if exists:
        self._table.update({"value": value}, cond=lambda row: row["key"] == key)
    else:
        self._table.insert({"key": key, "value": value})
```
- Si la clave ya existe → **actualiza** el valor (`update`).
- Si no existe → **inserta** un nuevo documento (`insert`).

Esto evita duplicados en la tabla — cada clave tiene exactamente un documento. TinyDB no tiene `upsert` nativo por clave propia, así que se implementa manualmente.

**Formato en disco (factpop.json):**
```json
{"app_config": {"1": {"key": "quiz_enabled", "value": true}, "2": {"key": "schedule_times", "value": ["09:00"]}}}
```
