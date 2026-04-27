# Etapa 5 — Fact History

| Archivo | Explicación |
|---|---|
| `factpop/features/history/models.py` | [models.md](models.md) |
| `factpop/features/history/repository.py` | [repository.md](repository.md) |
| `factpop/features/history/service.py` | [service.md](service.md) |
| `factpop/features/history/cli.py` | [cli.md](cli.md) |
| Tests (4 archivos, 36 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/features/history/
  models.py      ← FactRecord dataclass (id, topic, text, shown_at, example, saved)
  repository.py  ← TinyDBFactHistoryRepository con cap enforcement
  service.py     ← FactHistoryService (record, mark_saved, get_recent, count)
  cli.py         ← history list [--topic] [--saved-only]

tests/
  unit/features/
    test_fact_history_models.py    ← 5 tests
    test_fact_history_service.py   ← 12 tests (con freezegun)
    test_fact_history_cli.py       ← 5 tests
  integration/
    test_fact_history_repository.py ← 14 tests (con MemoryStorage)
```

## Decisiones clave

### Timestamp como string ISO 8601

Los timestamps se almacenan como strings `"2026-04-25T10:00:00"`. Esto permite:
- Ordenamiento correcto con comparación de strings (ISO 8601 ordena lexicográficamente igual que por fecha)
- Serialización directa en TinyDB JSON sin conversión
- `freezegun` puede controlar `datetime.now()` para tests determinísticos

### Cap enforcement en el repositorio

La lógica del cap (máx 500, evicción de no-saved) vive en el repositorio, no en el servicio. El repositorio es el guardián de la integridad de la tabla. Si algún módulo futuro inserta directamente al repositorio, el cap siempre se respeta.

### Importancia para Etapa 6 (Fact Generation)

`FactHistoryService` expone `get_recent(topic, limit)` que usará la Etapa 6 para:
1. **Deduplicación:** comparar el fact generado contra los últimos N facts del mismo topic
2. **Guardar el fact** después de generarlo exitosamente

## Gate de aceptación (todos pasan)

| Check | Resultado |
|---|---|
| `history list` | muestra todos los facts con topic, fecha, estado saved |
| `history list --topic Java` | solo facts de Java |
| `history list --saved-only` | solo facts marcados como saved |
| `history list` sin datos | hint de "no facts yet" |
| Cap de 3: insertar 4 (no saved) | el más antiguo se elimina, count=3 |
| Cap de 3: todos saved + insertar 1 | count=4, ningún saved eliminado |
| 182 tests totales | todos pasan (3 skipped por real LLM) |
