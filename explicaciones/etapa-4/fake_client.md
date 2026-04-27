# `factpop/shared/llm/fake.py` — `FakeLLMClient`

**Propósito:** Cliente LLM para tests que nunca hace llamadas de red. Configurable para responder con texto fijo o lanzar un error específico. Registra todos los prompts recibidos para hacer assertions.

```python
class FakeLLMClient:
    def __init__(
        self,
        response: str = "Fake LLM response.",
        error: LLMError | None = None,
    ) -> None:
        self._response = response
        self._error = error
        self.prompts_received: list[str] = []
        self.last_prompt: str | None = None
        self.call_count: int = 0
```

- `response` — el texto que devolverá `generate()`. Configurable por test.
- `error` — si se proporciona, `generate()` lanza ese error en vez de devolver el texto. Útil para testear el manejo de errores del llamador.
- `prompts_received` — lista de todos los prompts enviados. Útil para verificar que el servicio construyó el prompt correcto.
- `last_prompt` — shortcut para acceder al último prompt.
- `call_count` — cuántas veces se llamó `generate()`. Útil para verificar que no se llamó en exceso.

```python
def generate(self, prompt: str, *, model: str | None = None) -> str:
    self.prompts_received.append(prompt)
    self.last_prompt = prompt
    self.call_count += 1
    if self._error is not None:
        raise self._error
    return self._response
```

**Uso en tests de Etapa 5 (fact generation):**
```python
fake = FakeLLMClient(response="Java uses garbage collection for memory management.")
service = FactService(fake, topic_repo, history_repo)
fact = service.generate_fact("Java")
assert fake.last_prompt  # verifica que se envió un prompt
assert "Java" in fake.last_prompt  # verifica que el prompt menciona el tema
```

**Uso para simular error:**
```python
fake = FakeLLMClient(error=LLMTimeoutError("timed out"))
service = FactService(fake, ...)
fact = service.generate_fact("Java")
assert fact is None  # el servicio debe manejar el error y devolver None
```

Esta capacidad hace que `FakeLLMClient` sea la **herramienta principal de testing de toda la app** — toda la lógica de facts y quizzes se testea con este fake.
