# Tests de Etapa 8 (TDD) — 65 tests nuevos

## `test_review_repository.py` — 11 tests (integración)

Tests clave:
```python
def test_get_due_returns_item_due_today(repo) -> None:
    repo.insert(_item("f1", next_date="2026-04-25"))
    due = repo.get_due(as_of_date="2026-04-25")
    assert len(due) == 1  # items exactamente en la fecha contados

def test_get_due_excludes_resolved_items(repo) -> None:
    item.resolved = True; repo.update(item)
    assert repo.get_due(as_of_date="2026-04-25") == []
```

## `test_review_service.py` — 13 tests (con freezegun)

Tests de backoff:
```python
@freeze_time("2026-04-25")
def test_enqueue_same_fact_twice_uses_increment_fail(service) -> None:
    service.enqueue(record)
    service.enqueue(record)  # segundo fallo del mismo fact
    item = service.get_pending()[0]
    assert item.fail_count == 2
    assert item.next_review_date == "2026-04-27"  # today + 2

@freeze_time("2026-04-25")
def test_enqueue_caps_at_seven_days(service) -> None:
    for _ in range(10):
        service.enqueue(record)  # 10 fallos
    assert item.next_review_date == "2026-05-02"  # today + 7 (máximo)
```

## `test_quiz_prompts.py` — 13 tests

```python
def test_parse_correct_answer_b_gives_index_1() -> None:
    quiz = parse_quiz_response(_VALID_RESPONSE, source_fact_text=_SOURCE_FACT)
    assert quiz.correct_index == 1  # B = index 1 (0-indexed)

def test_parse_returns_none_when_fewer_than_four_options() -> None:
    malformed = "QUESTION: What?\nA: Option A\nB: Option B\nCORRECT: A"
    assert parse_quiz_response(malformed, source_fact_text=_SOURCE_FACT) is None
```

## `test_quiz_attempt_repository.py` — 6 tests (integración)

Verifican inserción, conteo y búsqueda por fact_id con todos los campos preservados.

## `test_quiz_service.py` — 17 tests

Tests de priorización de review queue:
```python
@freeze_time("2026-04-26")
def test_generate_uses_review_item_when_due() -> None:
    # review_svc.enqueue(records[0]) con freeze_time 2026-04-25
    # → next_review_date = 2026-04-26
    quiz = svc.generate(as_of_date="2026-04-26")
    assert quiz.from_review_queue is True
    assert quiz.source_fact.id == records[0].id

@freeze_time("2026-04-25")
def test_generate_does_not_use_review_item_before_due_date() -> None:
    review_svc.enqueue(records[0])  # due: 2026-04-26
    quiz = svc.generate(as_of_date="2026-04-25")  # un día antes
    assert quiz.from_review_queue is False  # no está due aún
```

Tests de grade:
```python
def test_grade_correct_on_review_item_resolves_it() -> None:
    # ... setup review item due today ...
    quiz = svc.generate(as_of_date="2026-04-26")
    svc.grade(quiz, selected_index=quiz.correct_index)
    assert review_svc.get_pending() == []  # resuelto, fuera de la queue

@freeze_time("2026-04-25")
def test_grade_incorrect_on_review_item_increments_fail() -> None:
    review_svc.enqueue(records[0])  # fail_count=1, next="2026-04-26"
    quiz = svc.generate(as_of_date="2026-04-26")
    svc.grade(quiz, selected_index=wrong_index)
    assert pending[0].fail_count == 2
    assert pending[0].next_review_date == "2026-04-27"  # today + 2
```

## `test_quiz_cli.py` — 8 tests

```python
def test_quiz_simulate_correct_answer_shows_correct(runner, monkeypatch, tmp_path) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    result = runner.invoke(app, ["quiz", "simulate"], input="2\n")  # B = correct
    assert "correct" in result.output.lower()

def test_quiz_simulate_wrong_answer_adds_to_review_queue(runner, monkeypatch, tmp_path) -> None:
    _add_facts(3)
    _patch_llm(monkeypatch)
    runner.invoke(app, ["quiz", "simulate"], input="1\n")  # wrong
    result = runner.invoke(app, ["reviews", "list"])
    assert "Java" in result.output  # fact aparece en review queue
```

El CliRunner acepta `input="2\n"` para simular entrada del usuario en el prompt de Typer. Esto permite testear el flujo interactivo completo sin necesidad de intervención manual.
