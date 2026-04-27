# `factpop/shared/llm/errors.py`

**Propósito:** Jerarquía de errores tipados para todas las fallas relacionadas con el LLM.

```
FactPopError
  └── LLMError              ← base de todos los errores LLM
        ├── LLMAuthError    ← API key ausente o rechazada por el proveedor
        ├── LLMTimeoutError ← la llamada superó el tiempo límite configurado
        └── LLMResponseError ← respuesta vacía, malformada o error HTTP inesperado
```

**¿Por qué tipos separados?**

- `LLMAuthError` → el usuario necesita revisar su `.env` (FACTPOP_API_KEY incorrecto).
- `LLMTimeoutError` → puede reintentarse o ignorarse en el intervalo actual (no es un error permanente).
- `LLMResponseError` → indica un problema con el proveedor o el modelo, no con la configuración.

El servicio de generación de facts (Etapa 5) capturará estos errores por separado para tomar decisiones distintas: loguear y saltar el popup en timeout/response, loguear + deshabilitar generación en auth error.
