# Etapa 4 — LLM Adapter + Secret Loading

| Archivo | Explicación |
|---|---|
| `factpop/shared/llm/errors.py` | [errors.md](errors.md) |
| `factpop/shared/llm/client.py` | [client_protocol.md](client_protocol.md) |
| `factpop/shared/llm/fake.py` | [fake_client.md](fake_client.md) |
| `factpop/shared/llm/openai_client.py` | [openai_client.md](openai_client.md) |
| `factpop/features/settings/secrets.py` | [secrets.md](secrets.md) |
| `factpop/shared/llm/cli.py` | [cli.md](cli.md) |
| Tests (4 archivos, 22 tests nuevos + 3 skipped→pasan con env var) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/
  shared/llm/
    errors.py        ← LLMError → LLMAuthError, LLMTimeoutError, LLMResponseError
    client.py        ← LLMClient Protocol (interfaz)
    fake.py          ← FakeLLMClient (tests: respuesta configurable + error configurable)
    openai_client.py ← OpenAICompatibleClient (producción: Venice AI / OpenAI / cualquier compatible)
    cli.py           ← factpop-cli llm ping
  features/settings/
    secrets.py       ← SecretStore Protocol + DotenvSecretStore + InMemorySecretStore

tests/
  unit/shared/
    test_secret_store.py      ← 8 tests
    test_fake_llm_client.py   ← 7 tests
  contract/
    test_llm_contract.py      ← 8 tests (3 requieren FACTPOP_TEST_REAL_LLM=1)
  unit/features/
    test_llm_cli.py           ← 2 tests
```

## Flujo de dependencias

```
LLM CLI (ping)
  → OpenAICompatibleClient
      → SecretStore (DotenvSecretStore en producción / InMemorySecretStore en tests)
      → openai.OpenAI(api_key, base_url)
          → /chat/completions
```

## Gate de aceptación (todos pasan)

| Check | Resultado |
|---|---|
| `llm ping` sin `.env` | Error: `FACTPOP_API_KEY is not set.` + exit 1 |
| `llm ping` con `.env` (Venice AI) | `Response: Pong` + exit 0 |
| Contract tests `[fake]` | 3/3 pasan |
| Contract tests `[real]` con `FACTPOP_TEST_REAL_LLM=1` | 3/3 pasan contra Venice AI |
| Auth error sin key | `LLMAuthError` lanzado correctamente |
| 146 tests totales | todos pasan (3 skipped en runs normales) |

## Nota de seguridad

El `.env` contiene la API key real y está en `.gitignore`. Los tests **nunca** leen el `.env` directamente — usan `InMemorySecretStore` con datos de prueba. La API key solo entra en tests de contrato reales vía `os.environ` (que el desarrollador cargó explícitamente).
