# `factpop/features/facts/prompts.py`

Dos funciones: una que construye el prompt y otra que parsea la respuesta del LLM.

---

## `build_fact_prompt(topic, recent_texts)`

```python
def build_fact_prompt(topic: str, recent_texts: list[str] | None = None) -> str:
```

**Opción A en acción:** el `topic` se usa verbatim. `"Java"`, `"AWS IAM - creacion de grupos de roles"` y `"¿Cómo funciona el recolector de basura en JVM?"` se pasan directamente al prompt.

**Estructura del prompt generado:**
```
You are a concise technical learning assistant.

Generate a short, useful learning fact about: {topic}

Requirements:
- Write a single clear, informative sentence as the fact.
- Optionally include a brief code or conceptual example (3 lines max).
- Total response MUST be under 150 words.
- Be specific and practical.

Respond ONLY in this exact format:
FACT: <your fact here>
EXAMPLE: <optional example, or omit this line entirely>

Avoid repeating or closely paraphrasing these recent facts already shown:
- {recent_text_1}
- {recent_text_2}
```

La sección "Avoid repeating" solo aparece si `recent_texts` es no vacía. Esto pasa los últimos N facts del mismo topic al LLM para que evite repetirlos.

---

## `parse_llm_response(raw) -> Fact | None`

Parsea la respuesta cruda del LLM en un objeto `Fact`.

```python
for line in raw.splitlines():
    stripped = line.strip()
    if stripped.upper().startswith("FACT:"):
        text = stripped[5:].strip()
        in_example = False
    elif stripped.upper().startswith("EXAMPLE:"):
        first_example_line = stripped[8:].strip()
        example_lines.append(first_example_line)
        in_example = True
    elif in_example and stripped:
        example_lines.append(stripped)  # captura líneas del ejemplo multiline
```

**Comportamientos:**
- `FACT:` en cualquier caso → extrae el texto
- `EXAMPLE:` en cualquier caso → extrae el ejemplo (multiline: sigue capturando líneas después)
- Sin `FACT:` → usa el response completo como texto (fallback graceful)
- Response vacío → `None`

**Ejemplos de respuestas del LLM que se parsean correctamente:**

```
FACT: Java uses StringBuilder for efficient string concatenation.
EXAMPLE: StringBuilder sb = new StringBuilder("Hello");
sb.append(" World");
```
→ `Fact(text="Java uses StringBuilder...", example="StringBuilder sb = ...\nsb.append...")`

```
Java is a strongly typed language with garbage collection.
```
→ `Fact(text="Java is a strongly typed language...", example=None)` (fallback)

```

```
→ `None`
