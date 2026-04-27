# `factpop/features/topics/errors.py`

**Propósito:** Define las excepciones de dominio específicas del módulo de topics. Cada error tiene un nombre que describe exactamente qué salió mal — sin tener que leer el mensaje.

---

```python
from factpop.shared.errors import FactPopError
```
Importa la excepción raíz de la app. Todas las excepciones de FactPop heredan de ella, lo que permite capturar cualquier error de dominio con `except FactPopError`.

---

```python
class EmptyTopicNameError(FactPopError):
    """Raised when a topic name is empty or contains only whitespace."""
```
Se lanza cuando el usuario intenta crear un tema con nombre vacío (`""`) o solo espacios (`"   "`). Al heredar de `FactPopError`, el CLI puede capturarla específicamente y mostrar un mensaje de validación apropiado.

```python
class DuplicateTopicError(FactPopError):
    """Raised when a topic with the same name (case-insensitive) already exists."""
```
Se lanza cuando se intenta crear un tema cuyo nombre ya existe en la base de datos (sin importar mayúsculas/minúsculas). Ej: si existe "Java", intentar crear "java" o "JAVA" lanza esta excepción.

```python
class TopicNotFoundError(FactPopError):
    """Raised when a topic cannot be found by name or id."""
```
Se lanza cuando se intenta activar, desactivar o eliminar un tema que no existe en la BD.

---

## ¿Por qué errores propios en vez de ValueError/KeyError?

| Usando ValueError | Usando TopicNotFoundError |
|---|---|
| `except ValueError` captura errores de parsing, casting, etc. | `except TopicNotFoundError` solo captura errores de topics |
| El mensaje hay que leerlo para saber qué pasó | El tipo del error ya comunica el problema |
| Difícil distinguir de errores de Python | Claramente un error de dominio de la app |

## Jerarquía

```
Exception
  └── FactPopError           (shared/errors.py)
        └── EmptyTopicNameError
        └── DuplicateTopicError
        └── TopicNotFoundError
```

El CLI captura cada error por separado para mostrar mensajes específicos al usuario.
