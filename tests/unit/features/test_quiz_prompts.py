from factpop.features.quizzes.prompts import build_quiz_prompt, parse_quiz_response


_SOURCE_FACT = "Java uses garbage collection to manage memory automatically."

_VALID_RESPONSE = (
    "QUESTION: What mechanism does Java use to manage memory?\n"
    "A: Manual deallocation\n"
    "B: Garbage collection\n"
    "C: Reference counting\n"
    "D: Stack-only allocation\n"
    "CORRECT: B"
)


# --- build_quiz_prompt ---

def test_prompt_includes_source_fact() -> None:
    prompt = build_quiz_prompt(_SOURCE_FACT)
    assert _SOURCE_FACT in prompt


def test_prompt_instructs_to_base_only_on_source_fact() -> None:
    prompt = build_quiz_prompt(_SOURCE_FACT).lower()
    assert "only" in prompt or "exclusively" in prompt or "based on" in prompt


def test_prompt_requests_four_options() -> None:
    prompt = build_quiz_prompt(_SOURCE_FACT)
    assert "4" in prompt or "four" in prompt.lower()


def test_prompt_requests_correct_answer_indicator() -> None:
    prompt = build_quiz_prompt(_SOURCE_FACT)
    assert "CORRECT:" in prompt


def test_prompt_requests_expected_format() -> None:
    prompt = build_quiz_prompt(_SOURCE_FACT)
    assert "QUESTION:" in prompt
    assert "A:" in prompt


# --- parse_quiz_response ---

def test_parse_extracts_question() -> None:
    quiz = parse_quiz_response(_VALID_RESPONSE, source_fact_text=_SOURCE_FACT)
    assert quiz is not None
    assert "memory" in quiz.question.lower()


def test_parse_extracts_four_options() -> None:
    quiz = parse_quiz_response(_VALID_RESPONSE, source_fact_text=_SOURCE_FACT)
    assert quiz is not None
    assert len(quiz.options) == 4


def test_parse_correct_answer_b_gives_index_1() -> None:
    quiz = parse_quiz_response(_VALID_RESPONSE, source_fact_text=_SOURCE_FACT)
    assert quiz is not None
    assert quiz.correct_index == 1  # B = index 1


def test_parse_correct_answer_a_gives_index_0() -> None:
    response = _VALID_RESPONSE.replace("CORRECT: B", "CORRECT: A")
    quiz = parse_quiz_response(response, source_fact_text=_SOURCE_FACT)
    assert quiz is not None
    assert quiz.correct_index == 0


def test_parse_correct_answer_d_gives_index_3() -> None:
    response = _VALID_RESPONSE.replace("CORRECT: B", "CORRECT: D")
    quiz = parse_quiz_response(response, source_fact_text=_SOURCE_FACT)
    assert quiz.correct_index == 3


def test_parse_options_preserve_text() -> None:
    quiz = parse_quiz_response(_VALID_RESPONSE, source_fact_text=_SOURCE_FACT)
    assert quiz is not None
    assert "Garbage collection" in quiz.options


def test_parse_returns_none_on_empty_response() -> None:
    assert parse_quiz_response("", source_fact_text=_SOURCE_FACT) is None
    assert parse_quiz_response("   ", source_fact_text=_SOURCE_FACT) is None


def test_parse_returns_none_when_fewer_than_four_options() -> None:
    malformed = "QUESTION: What?\nA: Option A\nB: Option B\nCORRECT: A"
    assert parse_quiz_response(malformed, source_fact_text=_SOURCE_FACT) is None
