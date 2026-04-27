from factpop.features.facts.prompts import build_fact_prompt, parse_llm_response


# --- build_fact_prompt ---

def test_prompt_includes_topic_name() -> None:
    prompt = build_fact_prompt("Java")
    assert "Java" in prompt


def test_prompt_works_with_specific_topic() -> None:
    prompt = build_fact_prompt("AWS IAM - creacion de grupos de roles")
    assert "AWS IAM - creacion de grupos de roles" in prompt


def test_prompt_instructs_concise_response() -> None:
    prompt = build_fact_prompt("Java")
    lowered = prompt.lower()
    assert "150" in lowered or "concise" in lowered or "short" in lowered


def test_prompt_requests_fact_and_optional_example() -> None:
    prompt = build_fact_prompt("Java")
    lowered = prompt.lower()
    assert "fact" in lowered
    assert "example" in lowered


def test_prompt_includes_format_instructions() -> None:
    prompt = build_fact_prompt("Java")
    assert "FACT:" in prompt
    assert "EXAMPLE:" in prompt


def test_prompt_includes_recent_texts_when_provided() -> None:
    recent = ["Java uses the JVM.", "Java is strongly typed."]
    prompt = build_fact_prompt("Java", recent_texts=recent)
    assert "Java uses the JVM." in prompt
    assert "Java is strongly typed." in prompt


def test_prompt_omits_recent_section_when_no_history() -> None:
    prompt = build_fact_prompt("Java", recent_texts=None)
    assert "avoid" not in prompt.lower() or "recent" not in prompt.lower()


def test_prompt_omits_recent_section_when_empty_list() -> None:
    prompt_with = build_fact_prompt("Java", recent_texts=["some fact"])
    prompt_without = build_fact_prompt("Java", recent_texts=[])
    assert len(prompt_with) > len(prompt_without)


# --- parse_llm_response ---

def test_parse_extracts_fact_and_example() -> None:
    raw = "FACT: Java uses the JVM.\nEXAMPLE: javac Hello.java"
    fact = parse_llm_response(raw)
    assert fact.text == "Java uses the JVM."
    assert fact.example == "javac Hello.java"


def test_parse_handles_missing_example() -> None:
    raw = "FACT: Java uses the JVM."
    fact = parse_llm_response(raw)
    assert fact.text == "Java uses the JVM."
    assert fact.example is None


def test_parse_falls_back_to_full_text_on_no_fact_prefix() -> None:
    raw = "Java is a strongly typed language with garbage collection."
    fact = parse_llm_response(raw)
    assert fact.text == raw
    assert fact.example is None


def test_parse_returns_none_on_empty_response() -> None:
    assert parse_llm_response("") is None
    assert parse_llm_response("   ") is None


def test_parse_strips_whitespace_from_fact_and_example() -> None:
    raw = "FACT:  Java uses the JVM.  \nEXAMPLE:  javac Hello.java  "
    fact = parse_llm_response(raw)
    assert fact.text == "Java uses the JVM."
    assert fact.example == "javac Hello.java"


def test_parse_multiline_example_is_preserved() -> None:
    raw = "FACT: Java is compiled.\nEXAMPLE: public class Hello {\n  public static void main(String[] args) {}\n}"
    fact = parse_llm_response(raw)
    assert fact.text == "Java is compiled."
    assert "public class Hello" in fact.example
