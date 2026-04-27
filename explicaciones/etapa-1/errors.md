# `factpop/shared/errors.py`

**Propósito:** Define la jerarquía base de excepciones personalizadas de FactPop.

---

```python
class FactPopError(Exception):
    """Root exception for all FactPop domain errors."""
```

**¿Por qué crear excepciones propias?**

Python tiene excepciones genéricas (`ValueError`, `RuntimeError`, etc.), pero crear una jerarquía propia tiene ventajas:

1. **Captura selectiva:** el código que usa la app puede hacer `except FactPopError` para capturar cualquier error de dominio de la app, sin atrapar errores de Python o de librerías externas.

2. **Documentación implícita:** al ver `raise FactPopError(...)` en el código, queda claro que es un error de negocio, no un bug de Python.

3. **Extensibilidad:** en etapas futuras, se agregan subclases específicas:
   ```python
   # (ejemplo futuro)
   class LLMError(FactPopError): ...
   class LLMTimeoutError(LLMError): ...
   class TopicNotFoundError(FactPopError): ...
   ```
   Estas subclases también son capturables con `except FactPopError` (por herencia), o de forma específica con `except LLMTimeoutError`.

4. **Filtrado en logs:** se puede configurar el logger para tratar errores de dominio diferente a errores inesperados del sistema.

**Herencia:**
```
Exception
  └── FactPopError          ← raíz de FactPop (este archivo)
        ├── LLMError        ← errores del cliente LLM (Etapa 4)
        │     ├── LLMTimeoutError
        │     ├── LLMAuthError
        │     └── LLMResponseError
        └── TopicError      ← errores de topics (Etapa 2)
              └── DuplicateTopicError
```
