# `factpop/features/history/models.py`

```python
@dataclass
class FactRecord:
    id: str
    topic: str
    text: str
    shown_at: str          # ISO 8601: "2026-04-25T10:00:00"
    example: str | None = field(default=None)
    saved: bool = field(default=False)
```

**Campos obligatorios** (sin default):
- `id` — UUID generado por el servicio al crear el registro
- `topic` — nombre del tema (ej: "Java")
- `text` — el fact mostrado al usuario
- `shown_at` — cuándo se mostró, en formato ISO 8601

**Campos opcionales** (con default):
- `example` — código o ejemplo adicional. `None` si el LLM no generó uno
- `saved` — el usuario marcó este fact como importante. `False` por defecto

**¿Por qué `shown_at` es string y no `datetime`?**

TinyDB serializa a JSON. `datetime` no es JSON-serializable directamente. Guardar como string ISO 8601 (`"2026-04-25T10:00:00"`) evita conversiones y permite ordenar lexicográficamente, ya que ISO 8601 preserva el orden cronológico como orden alfabético.
