# Etapa 8 — Quiz System

| Archivo | Explicación |
|---|---|
| `factpop/features/reviews/models.py` | [reviews.md](reviews.md) |
| `factpop/features/reviews/repository.py` | [reviews.md](reviews.md) |
| `factpop/features/reviews/interfaces.py` | [reviews.md](reviews.md) |
| `factpop/features/reviews/service.py` | [reviews.md](reviews.md) |
| `factpop/features/quizzes/models.py` | [quizzes.md](quizzes.md) |
| `factpop/features/quizzes/prompts.py` | [quizzes.md](quizzes.md) |
| `factpop/features/quizzes/repository.py` | [quizzes.md](quizzes.md) |
| `factpop/features/quizzes/service.py` | [quizzes.md](quizzes.md) |
| `factpop/features/quizzes/cli.py` | [cli.md](cli.md) |
| `factpop/features/reviews/cli.py` | [cli.md](cli.md) |
| Tests (6 archivos, 65 tests nuevos) | [tests.md](tests.md) |

## Estructura agregada

```
factpop/features/reviews/
  models.py       ← ReviewItem dataclass
  repository.py   ← TinyDBReviewRepository (insert, update, get_due, get_pending)
  interfaces.py   ← ReviewScheduler Protocol (consumido por QuizService)
  service.py      ← ReviewService (enqueue, increment_fail, resolve, get_due, get_pending)
  cli.py          ← reviews list

factpop/features/quizzes/
  models.py       ← Quiz + QuizAttempt dataclasses
  prompts.py      ← build_quiz_prompt() + parse_quiz_response()
  repository.py   ← TinyDBQuizAttemptRepository
  service.py      ← QuizService (generate, grade, skip)
  cli.py          ← quiz toggle on/off + quiz simulate [--date]
```

## Relación entre módulos

```
QuizService
  → FactHistoryService (get_recent para selección de facts)
  → ReviewScheduler (Protocol de reviews/) para enqueue/resolve/increment_fail/get_due
  → LLMClient (generar MCQ grounded en el source fact)
  → TinyDBQuizAttemptRepository (persistir intentos)
```

`QuizService` **depende de `ReviewScheduler` (protocolo)**, no de `ReviewService` directamente. Esto cumple el principio DIP: quizzes depende de una abstracción, no de la implementación concreta de reviews.

## Gate de aceptación

| Check | Resultado |
|---|---|
| `quiz simulate` con < 3 facts | "Not enough history..." |
| `quiz simulate` → respuesta incorrecta (1) | "Incorrect. Correct answer: Java" |
| `reviews list` después | item Java con `due: tomorrow, fails: 1` |
| `quiz simulate --date tomorrow` | usa el review item como fuente |
| `quiz simulate skip (s)` | no agrega a review queue |
| 304 tests totales | todos pasan (3 skipped real LLM) |

## Comportamiento de la review queue

```
1er fallo: next_review_date = today + 1
2do fallo: next_review_date = today + 2
...
7mo+ fallo: next_review_date = today + 7 (máximo)

Respuesta correcta en review item → resolved = True → sale de la queue
```
