# Tests de Etapa 6 (TDD) — 37 tests nuevos

## `test_fact_prompts.py` — 14 tests

Tests del sistema de prompts sin LLM real.

```python
def test_prompt_works_with_specific_topic() -> None:
    prompt = build_fact_prompt("AWS IAM - creacion de grupos de roles")
    assert "AWS IAM - creacion de grupos de roles" in prompt
```
Verifica la Opción A: el topic se usa verbatim, sin importar cuán específico sea.

```python
def test_parse_multiline_example_is_preserved() -> None:
    raw = "FACT: Java is compiled.\nEXAMPLE: public class Hello {\n  void main() {}\n}"
    fact = parse_llm_response(raw)
    assert fact.text == "Java is compiled."
    assert "public class Hello" in fact.example
```
Verifica que los ejemplos de código con múltiples líneas se capturan completos.

```python
def test_parse_falls_back_to_full_text_on_no_fact_prefix() -> None:
    raw = "Java is a strongly typed language with garbage collection."
    fact = parse_llm_response(raw)
    assert fact.text == raw
```
Si el LLM no sigue el formato exacto (sin `FACT:`), el texto completo se usa como fact. Robustez ante respuestas no-conformes.

---

## `test_fact_service.py` — 17 tests

Usan `FakeLLMClient` (Etapa 4) + TinyDB `MemoryStorage`.

### Tests de selección aleatoria

```python
def test_selected_topic_is_always_from_active_set() -> None:
    # Adds Java, Python, Kafka — runs generate 20 times
    for _ in range(20):
        result = svc.generate_and_record()
        assert result.topic in {"Java", "Python", "Kafka"}
```
No testea distribución uniforme (impracticable en unit test), pero sí que nunca se selecciona un topic fuera del conjunto activo.

### Tests de deduplicación — los más complejos

```python
class SequencedFakeLLM:
    def generate(self, prompt: str, *, model=None) -> str:
        r = responses[call_index % len(responses)]
        call_index += 1
        return r
```

`SequencedFakeLLM` devuelve respuestas en secuencia. Permite simular: "primera llamada devuelve similar, segunda devuelve distinto".

```python
# Test: retry con first == history (ratio 1.0, definitivamente similar)
original = "Java uses garbage collection to manage memory."
# history pre-populado con 'original'
# first LLM call: devuelve el mismo texto (ratio 1.0 → retry)
# second LLM call: devuelve texto distinto (se acepta)
assert llm.call_count >= 2
```

```python
# Test: dos intentos similares → se acepta el segundo sin más retry
similar1 = "FACT: Java uses garbage collection to manage memory."     # ratio ≈ 1.0
similar2 = "FACT: Java uses garbage collection to handle memory."     # devuelto como está
assert llm.call_count == 2  # exactamente 2 llamadas, no más
assert result is not None   # el segundo se usa aunque sea similar
assert history_svc.count() == 2  # guardado
```

### Por qué `similar1` debe ser genuinamente similar (≥ 0.85)

`SequenceMatcher` compara caracteres. Durante el REFACTOR se descubrió que los strings originales del test ("Java uses garbage collection for memory management.") solo alcanzaban ratio ~0.79 vs el original. Se actualizaron a strings prácticamente idénticos que sí superan 0.85.

---

## `test_fact_cli.py` — 6 tests

Usan `monkeypatch.setattr("factpop.features.facts.cli._build_llm", lambda: fake)` para reemplazar el LLM real por un `FakeLLMClient`.

```python
def test_cli_facts_generate_saves_to_history(runner, monkeypatch, tmp_path) -> None:
    runner.invoke(app, ["topics", "add", "Java"])
    llm = FakeLLMClient(response="FACT: Java has interfaces.")
    _patch_service(monkeypatch, llm)

    runner.invoke(app, ["facts", "generate"])
    result = runner.invoke(app, ["history", "list"])
    assert "Java" in result.output
```

Este test verifica el **flujo completo de integración** sin API real: CLI genera → CLI de history lo muestra. Es la prueba de que los módulos están correctamente conectados.
