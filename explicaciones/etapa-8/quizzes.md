# Quizzes — modelos, prompts, repositorio y servicio

## Modelos

**`Quiz`** — resultado del LLM antes de ser mostrado al usuario:
```python
@dataclass
class Quiz:
    source_fact: FactRecord    # fact en el que se basa la pregunta
    question: str
    options: list[str]         # exactamente 4
    correct_index: int         # 0-3
    from_review_queue: bool    # True = vino de la queue de revisión
```

**`QuizAttempt`** — persistido tras cada respuesta (no en skip):
```python
@dataclass
class QuizAttempt:
    id: str
    fact_id: str
    question: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    attempted_at: str
```

---

## `build_quiz_prompt()` — grounding en el fact fuente

El prompt instruye explícitamente al LLM a NO introducir información externa:
```
Based ONLY on the following fact, generate a multiple-choice question...
Rules:
- The question MUST be answerable using ONLY the information in the source fact.
- Do NOT introduce any information not present in the source fact.
```

Formato de respuesta esperado:
```
QUESTION: <pregunta>
A: <opción>
B: <opción>
C: <opción>
D: <opción>
CORRECT: B
```

## `parse_quiz_response()` — parser

Parsea línea por línea. Si hay menos de 4 opciones o `CORRECT:` no es A/B/C/D → devuelve `None` (respuesta malformada, el servicio la descarta sin mostrar quiz).

---

## `QuizService.generate()` — priorización de review queue

```python
def generate(self, as_of_date: str | None = None) -> Quiz | None:
    recent = self._history.get_recent(limit=50)
    if len(recent) < 3:
        return None  # insuficiente historial

    due_items = self._review.get_due(as_of_date=as_of_date)
    if due_items:
        source_fact, from_review = self._fact_from_review(due_items)
    else:
        source_fact = random.choice(recent)
        from_review = False
    ...
```

Si hay items vencidos en la review queue, se usa el primero como fuente. Si no, se elige un fact reciente al azar.

## `QuizService.grade()` — lógica de calificación y review queue

```python
is_correct = selected_index == quiz.correct_index

if is_correct and quiz.from_review_queue:
    self._review.resolve(quiz.source_fact.id)  # eliminado de la queue
elif not is_correct:
    if quiz.from_review_queue:
        self._review.increment_fail(quiz.source_fact.id)  # extiende el plazo
    else:
        self._review.enqueue(quiz.source_fact)  # agrega a la queue
```

4 casos posibles manejados explícitamente según si era review item y si fue correcta.
