# Tests de Etapa 4 (TDD)

## `tests/unit/shared/test_secret_store.py` — 8 tests

Verifican ambas implementaciones de `SecretStore`.

```python
def test_in_memory_get_returns_none_for_missing_key() -> None:
    store = InMemorySecretStore({})
    assert store.get("MISSING_KEY") is None
```

```python
def test_dotenv_store_reads_from_environment() -> None:
    with patch.dict(os.environ, {"FACTPOP_API_KEY": "sk-from-env"}):
        store = DotenvSecretStore()
        assert store.get("FACTPOP_API_KEY") == "sk-from-env"
```

`patch.dict(os.environ, {...})` modifica temporalmente `os.environ` solo para el bloque `with`. Al salir, restaura el estado original. Así los tests no afectan al entorno del desarrollador.

---

## `tests/unit/shared/test_fake_llm_client.py` — 7 tests

```python
def test_fake_client_can_be_configured_to_raise() -> None:
    client = FakeLLMClient(error=LLMError("simulated failure"))
    with pytest.raises(LLMError, match="simulated failure"):
        client.generate("any prompt")
```

Verifica que el `FakeLLMClient` puede simular errores. Este test es crucial porque en Etapa 5, el servicio de generación de facts necesita manejar `LLMError` correctamente, y los tests de esa etapa usarán esta capacidad.

---

## `tests/contract/test_llm_contract.py` — 8 tests (3 skipped en runs normales)

### Patrón de fixtures parametrizados

```python
@pytest.fixture(params=["fake", "real"])
def llm_client(request):
    if request.param == "fake":
        return FakeLLMClient(response="Java is a statically typed language.")
    if not os.getenv("FACTPOP_TEST_REAL_LLM"):
        pytest.skip("Set FACTPOP_TEST_REAL_LLM=1 to run real LLM contract tests")
    ...
    return OpenAICompatibleClient(_real_secrets())
```

`params=["fake", "real"]` hace que pytest ejecute cada test dos veces: una con el cliente fake, otra con el real. El `pytest.skip()` en el path `"real"` saltea automáticamente si la env var no está configurada.

**¿Por qué tests de contrato?**

Los tests de contrato verifican que tanto `FakeLLMClient` como `OpenAICompatibleClient` satisfacen el mismo contrato. Si el fake fuera distinto al real (ej: el fake devuelve string vacío pero el real nunca lo hace), los tests de etapas futuras estarían probando un comportamiento que no existe en producción.

```python
def test_generate_returns_non_empty_string(llm_client) -> None:
    result = llm_client.generate("Say hello in one word.")
    assert len(result.strip()) > 0
```

Este test fuerza que `FakeLLMClient` devuelva un string no vacío — si alguna implementación viola esta garantía, el fake también debe violarla (o actualizar el contrato).

### Tests de auth error (sin red)

```python
def test_openai_client_raises_auth_error_when_api_key_missing() -> None:
    secrets = InMemorySecretStore({"FACTPOP_API_KEY": ""})
    client = OpenAICompatibleClient(secrets)
    with pytest.raises(LLMAuthError, match="FACTPOP_API_KEY"):
        client.generate("hello")
```

Verifica el comportamiento con key vacía **sin llamar a la API real** — el error se lanza antes de cualquier conexión de red.

---

## `tests/unit/features/test_llm_cli.py` — 2 tests

```python
def test_cli_llm_ping_succeeds_with_valid_credentials(
    runner, monkeypatch
) -> None:
    fake = FakeLLMClient(response="pong")
    monkeypatch.setattr("factpop.shared.llm.cli._build_client", lambda: fake)
    result = runner.invoke(app, ["llm", "ping"])
    assert result.exit_code == 0
    assert "pong" in result.output
```

`monkeypatch.setattr` reemplaza `_build_client` (la función que crea el `OpenAICompatibleClient`) por una lambda que devuelve el fake. El CLI llama `_build_client()` internamente — al reemplazarla, el test controla qué cliente se usa sin llamar a la API real.

Esta es la **única excepción justificada al "no mocks"** de TDD: el CLI es el punto de integración que junta `DotenvSecretStore` + `OpenAICompatibleClient`. El comportamiento de ambos ya está testeado por separado; aquí solo se verifica que el CLI los usa correctamente.
