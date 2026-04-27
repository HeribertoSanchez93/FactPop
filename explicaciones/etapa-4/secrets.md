# `factpop/features/settings/secrets.py`

**Propósito:** Define cómo se leen los secretos (API key) y provee dos implementaciones: una para producción que lee del entorno del proceso, y otra para tests que usa un diccionario en memoria.

---

## `SecretStore` Protocol

```python
@runtime_checkable
class SecretStore(Protocol):
    def get(self, key: str, default: str | None = None) -> str | None: ...
```

Un protocolo de Python (`typing.Protocol`) define una **interfaz sin herencia**. Cualquier clase que tenga un método `get(key, default)` con esa firma cumple el protocolo automáticamente — no necesita heredar de `SecretStore`.

`@runtime_checkable` permite usar `isinstance(obj, SecretStore)` en runtime si fuera necesario.

---

## `DotenvSecretStore` (producción)

```python
class DotenvSecretStore:
    def get(self, key: str, default: str | None = None) -> str | None:
        value = os.environ.get(key)
        if value is None or value == "":
            return default
        return value
```

Lee de `os.environ`, que en producción contiene las variables cargadas por `load_dotenv()` al arrancar. Si el valor existe pero está vacío (`""`), trata el string vacío como ausente y devuelve el `default`. Esto evita que `FACTPOP_API_KEY=` (sin valor) cuele como key válida.

---

## `InMemorySecretStore` (tests)

```python
class InMemorySecretStore:
    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets

    def get(self, key: str, default: str | None = None) -> str | None:
        value = self._secrets.get(key)
        if value is None or value == "":
            return default
        return value
```

Implementación para tests. Se construye con un dict explícito, lo que hace los tests **herméticos** — no dependen del entorno del desarrollador ni del `.env` real.

**Uso en tests:**
```python
# Test con API key válida (fake)
secrets = InMemorySecretStore({"FACTPOP_API_KEY": "sk-test", "FACTPOP_BASE_URL": "..."})
client = OpenAICompatibleClient(secrets)

# Test con API key ausente
secrets = InMemorySecretStore({})
client = OpenAICompatibleClient(secrets)
# client.generate(...) → LLMAuthError
```

---

## ¿Por qué secretos separados de config?

En Etapa 3 se implementó `TinyDBSettingsRepository` para la configuración operativa (horarios, quiz enabled, etc.). Los secretos NO van ahí porque:
- TinyDB escribe a `factpop.json` — un archivo legible y potencialmente sincronizable a la nube.
- Los secretos solo deben vivir en `.env` (local, en `.gitignore`) o en el OS keyring (futuro).
- Separar la responsabilidad mantiene claro qué es configuración y qué es credencial.
