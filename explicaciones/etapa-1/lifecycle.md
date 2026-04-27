# `factpop/app/lifecycle.py`

**Propósito:** Garantiza que solo una instancia de FactPop esté corriendo a la vez. Si el usuario abre FactPop dos veces, la segunda sale inmediatamente con un mensaje claro. Usa un archivo de lock en disco como mecanismo de exclusión mutua.

---

```python
from __future__ import annotations
```
Habilita sintaxis de tipos moderna (`Path | None`, etc.) en Python 3.9+.

```python
import logging
```
Módulo estándar de Python para registrar mensajes (INFO, WARNING, ERROR) en el archivo de log.

```python
import sys
```
Módulo estándar para interactuar con el intérprete: aquí se usa `sys.exit(1)` para salir con código de error.

```python
from contextlib import contextmanager
```
Decorador que convierte una función generadora en un context manager (para usar con `with`). Permite escribir el código de setup y teardown juntos en un solo lugar.

```python
from pathlib import Path
```
Para manejar rutas del sistema de archivos.

```python
from typing import Generator
```
Tipo para anotar la función generadora del context manager.

```python
from filelock import FileLock, Timeout
```
- `FileLock` — crea un lock basado en un archivo en disco. Si el archivo de lock está tomado, otro proceso no puede tomarlo.
- `Timeout` — excepción que lanza `FileLock` cuando no puede adquirir el lock en el tiempo dado.

```python
from platformdirs import user_data_dir
```
Para obtener la carpeta de datos del usuario (mismo directorio que usa la DB).

---

```python
logger = logging.getLogger(__name__)
```
Crea un logger con el nombre del módulo (`factpop.app.lifecycle`). Buena práctica: cada módulo tiene su propio logger, y el nombre permite filtrar logs por origen.

---

```python
def _lock_path() -> Path:
    data_dir = Path(user_data_dir("FactPop"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "factpop.lock"
```
Devuelve la ruta del archivo de lock (ej: `C:\Users\PC\AppData\Local\FactPop\FactPop\factpop.lock`).
- El archivo de lock vive junto a la DB para que ambos estén en el mismo directorio de datos.
- El guión bajo `_lock_path` indica que es una función interna del módulo.

---

```python
@contextmanager
def instance_lock() -> Generator[None, None, None]:
```
Declara un context manager. El tipo `Generator[None, None, None]` indica:
- Primer `None` — tipo del valor que yieldeamos (nada en este caso).
- Segundo `None` — tipo del valor que se puede enviar al generador (no aplica).
- Tercer `None` — tipo del valor de retorno del generador (nada).

```python
    """Ensure only one FactPop process runs at a time.

    Exits with code 1 if another instance already holds the lock.
    """
```
Docstring que explica el comportamiento. Un lector puede entender qué hace sin leer el código.

```python
    lock = FileLock(str(_lock_path()), timeout=0)
```
Crea un objeto `FileLock` apuntando al archivo `.lock`. `timeout=0` significa que NO espera — si el lock está tomado, falla inmediatamente en vez de esperar.

```python
    try:
        lock.acquire(timeout=0)
    except Timeout:
        print(
            "FactPop is already running. Only one instance is allowed.",
            file=sys.stderr,
        )
        sys.exit(1)
```
- `lock.acquire(timeout=0)` — intenta tomar el lock. Si otro proceso ya lo tiene, lanza `Timeout`.
- En el `except Timeout`: imprime el mensaje de error en `stderr` (canal de errores, no stdout) y llama `sys.exit(1)`. El código `1` indica error (convención Unix/Windows).
- `sys.exit(1)` lanza `SystemExit`, que Python propaga hacia arriba y termina el proceso.

```python
    logger.info("FactPop instance started (lock acquired at %s)", _lock_path())
```
Registra en el log que esta instancia arrancó correctamente. El `%s` es formateo lazy de logging (más eficiente que f-strings porque no construye el string si el nivel de log está desactivado).

```python
    try:
        yield
    finally:
        lock.release()
        logger.info("FactPop instance stopped (lock released)")
```
- `yield` — aquí se ejecuta el bloque `with instance_lock(): ...` del código llamador.
- `finally` — se ejecuta siempre al salir del `with`, ya sea por Ctrl+C, excepción, o salida normal.
- `lock.release()` — libera el archivo de lock para que otra instancia pueda arrancarse después.
- El log de "stopped" confirma que el shutdown fue limpio.

---

**Flujo completo:**

```
python -m factpop (primera vez)
  → lock.acquire() → OK → yield → app corre...
  → Ctrl+C → finally → lock.release() → app termina limpia

python -m factpop (segunda vez, mientras la primera corre)
  → lock.acquire() → Timeout → print error → sys.exit(1) → termina inmediatamente
```
