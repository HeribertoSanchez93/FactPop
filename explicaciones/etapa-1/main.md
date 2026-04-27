# `factpop/__main__.py` y `factpop/app/__main__.py`

Hay dos archivos `__main__.py`. Esto es intencional — cada uno tiene un rol distinto.

---

## `factpop/__main__.py` — Punto de entrada del comando `python -m factpop`

```python
from factpop.app.__main__ import main

main()
```

**¿Por qué existe este archivo?**

Cuando el usuario ejecuta `python -m factpop`, Python busca un archivo `__main__.py` directamente en el paquete `factpop/`. Este archivo actúa como "puerta de entrada" y delega inmediatamente al `main()` real que vive en `factpop/app/__main__.py`.

- Sin este archivo → `python: No module named factpop.__main__; 'factpop' is a package and cannot be directly executed`
- Con este archivo → el comando funciona

Es un archivo de una sola responsabilidad: redirigir. La lógica real está en otro lado.

---

## `factpop/app/__main__.py` — Lógica de arranque del daemon

**Propósito:** Secuencia de arranque de la aplicación. Inicializa los sistemas base en orden correcto y mantiene el proceso vivo hasta que el usuario lo detenga.

```python
from __future__ import annotations
```
Tipos modernos.

```python
import logging
import time
```
- `logging` — para obtener el logger de este módulo.
- `time` — para `time.sleep(1)`, que mantiene el proceso vivo sin consumir CPU.

```python
from dotenv import load_dotenv
```
Importa la función que lee el archivo `.env` y carga sus variables en el entorno del proceso (en `os.environ`). Debe llamarse antes de cualquier código que use esas variables.

```python
from factpop.app.bootstrap import bootstrap
from factpop.app.lifecycle import instance_lock
from factpop.shared.logging_config import setup_logging
from factpop.shared.storage.tinydb_factory import close_db, init_db
```
Importa los sistemas que vamos a inicializar en orden.

---

```python
logger = logging.getLogger(__name__)
```
Logger para este módulo específico (`factpop.app.__main__`).

---

```python
def main() -> None:
```
Función principal. Toda la lógica de arranque vive aquí en vez de estar suelta a nivel de módulo — esto permite importar el archivo sin ejecutar nada automáticamente.

```python
    load_dotenv()
```
**Primera línea que se ejecuta.** Lee `.env` del directorio actual y pone `FACTPOP_API_KEY`, `FACTPOP_BASE_URL`, etc. en `os.environ`. Debe ser lo primero para que todo lo que viene después pueda leer esas variables.

Si `.env` no existe, `load_dotenv()` no falla — simplemente no hace nada.

```python
    setup_logging()
```
**Segunda.** Configura los handlers de log. Debe hacerse antes de cualquier `logger.info(...)` para que los mensajes no se pierdan.

```python
    with instance_lock():
```
**Tercera.** Adquiere el lock de instancia única. Si otro proceso ya tiene el lock, aquí la app sale con código 1 y el bloque `with` nunca se ejecuta. Todo el código dentro de `with instance_lock():` corre con la garantía de ser la única instancia.

```python
        db = init_db()
```
Abre (o crea) la base de datos TinyDB y registra las 5 tablas. La variable `db` no se usa directamente aquí, pero la llamada garantiza que la DB esté lista antes de que cualquier servicio la necesite.

```python
        bootstrap()
```
Llama al módulo de wiring. En Etapa 1 no hace nada, pero en etapas futuras aquí se construirán y conectarán todos los servicios (scheduler, notificaciones, etc.).

```python
        logger.info("FactPop started. Press Ctrl+C to stop.")
```
Registra en el log que el arranque fue exitoso. El usuario puede verificarlo en `factpop.log`.

```python
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user.")
```
- `while True: time.sleep(1)` — mantiene el proceso vivo durmiendo 1 segundo a la vez. En el futuro, el scheduler correrá en un hilo separado y este loop podrá ser reemplazado por el loop del tray icon (pystray).
- `time.sleep(1)` en vez de `time.sleep(0)` → sin `sleep`, el loop gastaría el 100% de un núcleo de CPU sin hacer nada.
- `except KeyboardInterrupt` → captura Ctrl+C para hacer un shutdown limpio en vez de un error inesperado.

```python
        finally:
            close_db()
```
`finally` se ejecuta siempre al salir del `try`, ya sea por Ctrl+C, excepción, o salida normal. `close_db()` cierra el archivo JSON correctamente.

---

**Orden de arranque completo:**

```
python -m factpop
  1. load_dotenv()          ← carga .env en os.environ
  2. setup_logging()        ← configura file + console handlers
  3. instance_lock()        ← adquiere lock (o sale si ya está tomado)
  4. init_db()              ← abre TinyDB y crea tablas
  5. bootstrap()            ← construye servicios (vacío en Etapa 1)
  6. while True: sleep(1)   ← mantiene vivo hasta Ctrl+C
  7. finally: close_db()    ← cierra DB al salir
  8. instance_lock finally  ← libera el lock
```
