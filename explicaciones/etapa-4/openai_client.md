# `factpop/shared/llm/openai_client.py` — `OpenAICompatibleClient`

**Propósito:** Implementación de producción del adaptador LLM. Soporta cualquier API compatible con el formato OpenAI (Venice AI, OpenAI, Azure OpenAI, Ollama con modo OpenAI, LM Studio, etc.) configurando solo `FACTPOP_BASE_URL`.

---

```python
def __init__(self, secrets: SecretStore) -> None:
    self._secrets = secrets
```

Recibe el `SecretStore` por constructor (DI). Esto permite:
- Producción: `OpenAICompatibleClient(DotenvSecretStore())`
- Tests: `OpenAICompatibleClient(InMemorySecretStore({...}))`

---

```python
def generate(self, prompt: str, *, model: str | None = None) -> str:
    api_key = self._secrets.get("FACTPOP_API_KEY")
    if not api_key:
        raise LLMAuthError("FACTPOP_API_KEY is not set. Add it to your .env file.")
```

**Primera verificación:** si no hay API key, falla rápido con `LLMAuthError` antes de intentar ninguna conexión de red.

```python
    base_url = self._secrets.get("FACTPOP_BASE_URL") or _DEFAULT_BASE_URL
    model_name = model or self._secrets.get("FACTPOP_MODEL") or _DEFAULT_MODEL
    timeout = float(self._secrets.get("FACTPOP_LLM_TIMEOUT_SECONDS") or _DEFAULT_TIMEOUT)
```

Lee la configuración con fallback a defaults razonables. El operador `or` en Python devuelve el primer valor truthy — si `get()` devuelve `None` o string vacío, usa el default.

```python
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
```

Crea el cliente de openai por llamada (no se cachea). Esto permite cambiar la API key en el `.env` y reiniciar la app sin que el cliente use la key vieja.

```python
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        timeout=timeout,
        max_tokens=500,
    )
```

Llama al endpoint `/chat/completions` del proveedor. `max_tokens=500` limita la respuesta para evitar respuestas excesivamente largas en popups.

```python
    except openai.AuthenticationError as exc:
        raise LLMAuthError(str(exc)) from exc
    except openai.APITimeoutError as exc:
        raise LLMTimeoutError(str(exc)) from exc
    except openai.APIError as exc:
        raise LLMResponseError(str(exc)) from exc
```

**Mapeo de errores:** las excepciones de `openai` SDK se convierten en errores propios de la app (`LLMError`). Así la lógica de negocio (Etapas 5+) no necesita importar `openai` — solo maneja `LLMError`. Si mañana se cambia de proveedor, este mapeo también cambia.

---

## Configuración para Venice AI

```env
FACTPOP_API_KEY=VENICE_INFERENCE_KEY_...
FACTPOP_BASE_URL=https://api.venice.ai/api/v1
FACTPOP_MODEL=venice-uncensored
```

El SDK de openai llama automáticamente a `https://api.venice.ai/api/v1/chat/completions`. No se necesita código especial — el `base_url` hace todo el trabajo.

## Para cambiar de proveedor

Solo cambia el `.env`:
```env
# Anthropic (via proxy compatible)
FACTPOP_BASE_URL=https://api.anthropic.com/v1
FACTPOP_MODEL=claude-3-haiku-20240307

# Ollama local
FACTPOP_BASE_URL=http://localhost:11434/v1
FACTPOP_MODEL=llama3
FACTPOP_API_KEY=ollama  # Ollama no requiere key real
```
