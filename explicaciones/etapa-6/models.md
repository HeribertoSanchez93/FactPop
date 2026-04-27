# `factpop/features/facts/models.py` — `Fact`

```python
@dataclass
class Fact:
    """Parsed LLM response before being persisted as a FactRecord."""
    topic: str
    text: str
    example: str | None = field(default=None)
```

`Fact` es el objeto **intermedio** entre el LLM y la persistencia:

```
LLM response (raw string)
    ↓ parse_llm_response()
Fact(topic, text, example)   ← este modelo
    ↓ history.record()
FactRecord(id, topic, text, shown_at, example, saved)   ← persistido
```

**¿Por qué existe si FactRecord ya tiene los mismos campos?**

- `FactRecord` tiene `id`, `shown_at`, y `saved` — campos que solo existen después de persistir
- `Fact` representa "lo que el LLM generó" antes de decidir si guardarlo
- El `topic` en `Fact` se asigna después del parsing (línea `fact.topic = topic`) porque `parse_llm_response()` no sabe a qué topic pertenece
- Separar los dos modelos hace el código más legible: el parser no mezcla lógica de persistencia
