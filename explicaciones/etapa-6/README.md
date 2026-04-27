# Etapa 6 — Fact Generation

| Archivo | Explicación |
|---|---|
| `factpop/features/facts/models.py` | [models.md](models.md) |
| `factpop/features/facts/prompts.py` | [prompts.md](prompts.md) |
| `factpop/features/facts/service.py` | [service.md](service.md) |
| `factpop/features/facts/cli.py` | [cli.md](cli.md) |
| Tests (3 archivos, 37 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/features/facts/
  models.py    ← Fact dataclass (resultado intermedio del LLM antes de persistir)
  prompts.py   ← build_fact_prompt() + parse_llm_response()
  service.py   ← FactService (orquesta: topic selection → LLM → dedup → history)
  cli.py       ← facts generate [--topic]

tests/unit/features/
  test_fact_prompts.py   ← 14 tests (prompt builder + parser)
  test_fact_service.py   ← 17 tests (con FakeLLMClient + MemoryStorage)
  test_fact_cli.py       ← 6 tests
```

## Flujo completo

```
factpop-cli facts generate [--topic "AWS IAM - creacion de grupos de roles"]
         ↓
  FactService.generate_and_record(topic_name)
         ↓
  1. _resolve_topic() → "Java" (random) OR "AWS IAM - creacion de grupos de roles" (explicit)
         ↓
  2. history.get_recent(topic, limit=10) → recent_texts para dedup
         ↓
  3. build_fact_prompt(topic, recent_texts) → prompt estructurado
         ↓
  4. llm.generate(prompt) → "FACT: ...\nEXAMPLE: ..."
         ↓
  5. parse_llm_response() → Fact(text=..., example=...)
         ↓
  6. Dedup check: similar a algún recent? → retry once si sí
         ↓
  7. history.record(topic, text, example) → FactRecord persistido
         ↓
  8. CLI imprime: [topic] fact text \n Example: ...
```

## Decisión de diseño: Option A para topics

El nombre del topic es texto libre. Los prompts funcionan igual con:
- `"Java"` → el LLM elige qué aspecto de Java enseñar
- `"AWS IAM - creacion de grupos de roles"` → el LLM focaliza en ese tema específico
- `"Spring Boot con Kafka"` → el LLM genera facts sobre esa combinación

Sin cambios en el data model de topics. El usuario controla la granularidad al nombrar sus topics.

## Gate de aceptación (verificado con Venice AI)

| Check | Resultado |
|---|---|
| `facts generate` (random) | `[Java] In Java, StringBuilder...` con ejemplo |
| `facts generate --topic "AWS IAM..."` | Fact específico sobre IAM con policy JSON |
| Sin topics activos | Error + exit 1 |
| LLM error | Error + exit 1, sin guardar en history |
| `history list` después | Muestra los facts generados |
| 219 tests totales | todos pasan (3 skipped real LLM) |
