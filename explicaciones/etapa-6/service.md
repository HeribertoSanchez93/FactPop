# `factpop/features/facts/service.py`

**Propósito:** Orquestador central de la generación de facts. Conecta selección de topic, llamada al LLM, deduplicación, y persistencia en history.

**Recibe por constructor (DIP):**
- `TopicService` — para `list_active()` y selección random
- `FactHistoryService` — para `get_recent()` (dedup) y `record()` (persistencia)
- `LLMClient` — adaptador intercambiable (OpenAI, Venice, Fake)
- `dedupe_window` — cuántos facts recientes comparar (default 10)

---

## `generate_and_record(topic_name=None) -> FactRecord | None`

Retorna `None` sin guardar en historial cuando:
- No hay topics activos (y no se pasó `topic_name`)
- El LLM lanza un error (`LLMError`)
- El LLM devuelve texto vacío o sin parsear

### Paso 1: `_resolve_topic()`

```python
def _resolve_topic(self, topic_name: str | None) -> str | None:
    if topic_name is not None:
        return topic_name
    active = self._topics.list_active()
    if not active:
        return None
    return random.choice(active).name
```

`random.choice()` da distribución uniforme — cada topic activo tiene la misma probabilidad.

### Paso 2: Construir el prompt con contexto de dedup

```python
recent = self._history.get_recent(topic=topic, limit=self._dedupe_window)
recent_texts = [r.text for r in recent]
prompt = build_fact_prompt(topic, recent_texts=recent_texts or None)
```

Los últimos `dedupe_window` facts del mismo topic se pasan al LLM para que los evite. `or None` convierte lista vacía a `None` (omite la sección del prompt).

### Paso 3: `_call_llm_with_dedup()`

```python
raw = self._call_llm(prompt)     # primera llamada
fact = parse_llm_response(raw)   # parsear

# Dedup check
if recent_texts and any(_is_similar(fact.text, t) for t in recent_texts):
    retry_raw = self._call_llm(prompt)   # segunda llamada (máximo)
    retry_fact = parse_llm_response(retry_raw)
    if retry_fact is not None:
        fact = retry_fact  # usar segunda respuesta sin importar similaridad
```

Solo se hace UN retry. Si el segundo también es similar, se usa igual. La spec dice "one additional generation attempt; if the second is also similar, it proceeds."

### Dedup con `SequenceMatcher`

```python
_SIMILARITY_THRESHOLD = 0.85

def _is_similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= _SIMILARITY_THRESHOLD
```

`SequenceMatcher` compara secuencias de caracteres (no palabras). A 0.85 de threshold, strings que comparten ~85% de su contenido se consideran duplicados. Funciona bien para frases técnicas que son variaciones de la misma idea.

### Paso 4: Persistir

```python
return self._history.record(
    topic=topic,
    text=fact.text,
    example=fact.example,
)
```

Solo se persiste si llegamos aquí — si `_call_llm_with_dedup` devuelve `None`, no hay persistencia.

---

## `_call_llm()` — captura errores

```python
def _call_llm(self, prompt: str) -> str | None:
    try:
        return self._llm.generate(prompt)
    except LLMError as exc:
        logger.error("LLM call failed: %s", exc)
        return None
```

Captura cualquier `LLMError` (auth, timeout, response). Retorna `None` en vez de propagar — el servicio decide qué hacer (skip popup). La lógica de negocio no propaga errores técnicos del LLM.
