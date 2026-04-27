# `factpop/shared/logging_config.py`

**Propósito:** Configura el sistema de logging de la app una sola vez al arrancar. Define que los mensajes de log vayan tanto a un archivo rotatorio en disco como a la consola.

---

```python
from __future__ import annotations
```
Sintaxis de tipos modernos en Python 3.9+.

```python
import logging
import logging.handlers
```
- `logging` — módulo estándar para registrar mensajes con niveles (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `logging.handlers` — submódulo con handlers especializados, en particular `RotatingFileHandler`.

```python
from pathlib import Path
```
Para construir la ruta del archivo de log de forma segura.

```python
from platformdirs import user_log_dir
```
Devuelve la carpeta de logs del usuario según el SO:
- Windows → `C:\Users\PC\AppData\Local\FactPop\FactPop\Logs`
- macOS → `~/Library/Logs/FactPop`

---

```python
_FORMAT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
```
Plantilla de formato para los mensajes de log:
- `%(asctime)s` — fecha y hora (ej: `2026-04-24T18:36:15`)
- `%(levelname)-8s` — nivel del mensaje con padding a 8 chars (ej: `INFO    `, `WARNING `)
- `%(name)s` — nombre del logger (ej: `factpop.app.lifecycle`)
- `%(message)s` — el texto del mensaje

Ejemplo de línea real: `2026-04-24T18:36:15 INFO     factpop.app.lifecycle — FactPop instance started`

```python
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
```
Formato ISO 8601 para la fecha (año-mes-día T hora:minuto:segundo). Fácil de ordenar y parsear.

---

```python
def setup_logging(level: int = logging.INFO) -> None:
```
Función principal. `level` controla qué tan detallados son los logs:
- `logging.DEBUG` (10) — todo
- `logging.INFO` (20) — operaciones normales (default)
- `logging.WARNING` (30) — solo advertencias y errores
- `-> None` — no devuelve nada

```python
    log_dir = Path(user_log_dir("FactPop"))
    log_dir.mkdir(parents=True, exist_ok=True)
```
Obtiene y crea la carpeta de logs si no existe.

```python
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "factpop.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
```
Crea un handler que escribe a un archivo y lo rota automáticamente:
- `log_dir / "factpop.log"` — ruta completa del archivo de log.
- `maxBytes=5 * 1024 * 1024` — cuando el archivo llega a 5 MB, se crea uno nuevo.
- `backupCount=3` — guarda hasta 3 archivos viejos (`factpop.log.1`, `.2`, `.3`). El cuarto se borra.
- `encoding="utf-8"` — soporta caracteres especiales (tildes, emojis, etc.).

**¿Por qué rotar?** Sin rotación, el log crecería indefinidamente. Con esta config se mantienen máximo `5 MB × 4 archivos = 20 MB` de historial.

```python
    file_handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))
```
Aplica el formato definido arriba al archivo de log.

```python
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s — %(message)s"))
```
- `StreamHandler()` — escribe los logs en la consola (stdout/stderr).
- El formato de consola es más corto que el del archivo (sin timestamp, ya lo ve el usuario en pantalla).

```python
    root = logging.getLogger()
```
Obtiene el logger raíz de Python. Todos los loggers de la app (`logging.getLogger("factpop.xxx")`) heredan del raíz.

```python
    root.setLevel(level)
```
Establece el nivel mínimo. Los mensajes por debajo de este nivel se descartan sin procesar.

```python
    root.addHandler(file_handler)
    root.addHandler(console_handler)
```
Registra ambos handlers. A partir de aquí, cualquier `logging.getLogger("factpop.xxx").info("msg")` en cualquier parte de la app escribirá al archivo Y a la consola.

---

**Flujo de un mensaje de log:**

```
logger.info("FactPop started")
  → root logger (level INFO) → pasa el filtro
  → file_handler → escribe en factpop.log con timestamp
  → console_handler → imprime en consola sin timestamp
```
