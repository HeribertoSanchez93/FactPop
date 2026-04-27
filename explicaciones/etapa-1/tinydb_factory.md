# `factpop/shared/storage/tinydb_factory.py`

**Propósito:** Crea y gestiona la conexión única (singleton) a la base de datos TinyDB. Todo el resto de la app obtiene su instancia de DB a través de este módulo — nunca crea TinyDB directamente.

---

```python
from __future__ import annotations
```
Permite usar tipos como `Path | None` en Python 3.9 sin errores. En 3.10+ ya es nativo, pero se pone por compatibilidad y claridad.

```python
from pathlib import Path
```
Importa `Path` para manejar rutas del sistema de archivos de forma segura (en vez de concatenar strings con `\` o `/`).

```python
from platformdirs import user_data_dir
```
Importa una función que devuelve la carpeta de datos del usuario según el SO:
- Windows → `C:\Users\PC\AppData\Local\FactPop\FactPop`
- macOS → `~/Library/Application Support/FactPop`
- Linux → `~/.local/share/FactPop`

```python
from tinydb import TinyDB
```
Importa la clase principal de TinyDB, la base de datos NoSQL local basada en archivos JSON.

---

```python
_TABLES = ("topics", "app_config", "fact_history", "quiz_attempts", "review_queue")
```
Define los nombres de las 5 tablas que usará la app. El guión bajo `_` indica que es privado al módulo (convención de Python). Es una tupla (inmutable) porque los nombres nunca cambian.

```python
_db: TinyDB | None = None
```
Variable global del módulo que guarda la instancia única de TinyDB. Empieza en `None` (sin conexión). El tipo `TinyDB | None` indica que puede ser una instancia de TinyDB o nada.

---

```python
def _data_path() -> Path:
    data_dir = Path(user_data_dir("FactPop"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "factpop.json"
```
- `user_data_dir("FactPop")` — pregunta al SO cuál es la carpeta correcta para datos de "FactPop".
- `Path(...)` — convierte el string a un objeto `Path` manejable.
- `.mkdir(parents=True, exist_ok=True)` — crea la carpeta si no existe. `parents=True` crea también las carpetas padre. `exist_ok=True` no falla si ya existe.
- `data_dir / "factpop.json"` — construye la ruta completa del archivo de base de datos.

---

```python
def get_db() -> TinyDB:
    global _db
    if _db is None:
        _db = TinyDB(str(_data_path()))
    return _db
```
- `global _db` — indica que vamos a modificar la variable global, no crear una local.
- `if _db is None` — si aún no hay conexión abierta, la creamos.
- `TinyDB(str(_data_path()))` — abre (o crea) el archivo JSON. TinyDB necesita el path como string.
- `return _db` — devuelve la instancia (ya sea recién creada o la existente).

**Patrón:** Singleton perezoso — la conexión solo se abre cuando alguien la pide por primera vez.

---

```python
def init_db(path: Path | None = None) -> TinyDB:
    global _db
    if _db is None:
        resolved = path if path is not None else _data_path()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        _db = TinyDB(str(resolved))
    for table_name in _TABLES:
        _db.table(table_name)
    return _db
```
- `path: Path | None = None` — parámetro opcional. En producción no se pasa (usa la ruta real). En tests se pasa `tmp_path / "test.json"` para no tocar datos reales.
- `resolved = path if path is not None else _data_path()` — usa el path recibido si hay uno, si no usa el del SO.
- `resolved.parent.mkdir(...)` — se asegura que la carpeta padre exista (necesario cuando `path` viene de fuera).
- `for table_name in _TABLES: _db.table(table_name)` — accede a cada tabla para que queden registradas. TinyDB las crea en el JSON en el primer insert, no aquí.
- `return _db` — devuelve la instancia lista para usar.

**Diferencia con `get_db()`:** `init_db` acepta un path personalizado y garantiza que las tablas estén registradas. Es la función de arranque; `get_db` es para acceso rápido después de inicializar.

---

```python
def close_db() -> None:
    global _db
    if _db is not None:
        _db.close()
        _db = None
```
- `if _db is not None` — solo cierra si hay una conexión abierta (evita error al llamar dos veces).
- `_db.close()` — cierra el archivo JSON correctamente, guardando cualquier write pendiente.
- `_db = None` — resetea el singleton para que la próxima llamada a `get_db()` o `init_db()` abra una conexión nueva.

**Por qué importa:** Sin `close_db()`, el archivo puede quedar en estado inconsistente si la app se cierra abruptamente. También, en tests, `close_db()` libera el archivo entre pruebas.
