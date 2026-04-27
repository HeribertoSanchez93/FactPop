# `factpop/shared/llm/client.py` — `LLMClient` Protocol

**Propósito:** Define el contrato mínimo que cualquier cliente LLM debe cumplir. Este es el borde de la "capa de adaptador" — todo el código de la app interactúa con `LLMClient`, nunca con `openai.OpenAI` directamente.

```python
@runtime_checkable
class LLMClient(Protocol):
    def generate(self, prompt: str, *, model: str | None = None) -> str: ...
```

**Un solo método.** El protocolo es intencionalmente pequeño (Interface Segregation Principle). Solo se necesita enviar un prompt y recibir texto. Si en el futuro se necesita streaming o embeddings, será un protocolo separado — no se agrega aquí.

**`model: str | None = None`** — parámetro keyword-only (`*`) que permite sobreescribir el modelo por llamada. Cuando es `None`, la implementación usa el modelo configurado en `FACTPOP_MODEL`.

**¿Por qué Protocol y no ABC?**

| ABC (clase abstracta) | Protocol (duck typing) |
|---|---|
| `FakeLLMClient(LLMClient)` — herencia requerida | `FakeLLMClient` — no hereda de nada |
| Acoplamiento entre fake y la interfaz | Fake es independiente |
| Cambiar la interfaz puede romper la cadena de herencia | Cambiar Protocol solo afecta a las implementaciones |

El `Protocol` es más flexible y no crea acoplamiento innecesario. `FakeLLMClient` cumple el protocolo simplemente por tener el método correcto.
