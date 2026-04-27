from __future__ import annotations

from factpop.features.facts.models import Fact

_FACT_PREFIX = "FACT:"
_EXAMPLE_PREFIX = "EXAMPLE:"


def build_fact_prompt(topic: str, recent_texts: list[str] | None = None) -> str:
    """Build the LLM prompt for generating a learning fact about a topic.

    The topic name is used verbatim (Option A) — users can name their topics
    as broadly or specifically as they want, e.g. "Java", "AWS IAM role groups".
    """
    lines = [
        f"You are a concise technical learning assistant.",
        f"",
        f"Generate a short, useful learning fact about: {topic}",
        f"",
        f"Requirements:",
        f"- Write a single clear, informative sentence as the fact.",
        f"- Optionally include a brief code or conceptual example (3 lines max).",
        f"- Total response MUST be under 150 words.",
        f"- Be specific and practical.",
        f"",
        f"Respond ONLY in this exact format:",
        f"FACT: <your fact here>",
        f"EXAMPLE: <optional example, or omit this line entirely>",
    ]

    if recent_texts:
        lines += [
            f"",
            f"Avoid repeating or closely paraphrasing these recent facts already shown:",
        ]
        for text in recent_texts:
            lines.append(f"- {text}")

    return "\n".join(lines)


def parse_llm_response(raw: str) -> Fact | None:
    """Parse the LLM response into a Fact.

    Expected format:
        FACT: <text>
        EXAMPLE: <optional example>

    Falls back to using the entire response as the fact text if no FACT: prefix found.
    Returns None if the response is empty or whitespace-only.
    """
    if not raw or not raw.strip():
        return None

    text: str | None = None
    example_lines: list[str] = []
    in_example = False

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith(_FACT_PREFIX):
            text = stripped[len(_FACT_PREFIX):].strip()
            in_example = False
        elif stripped.upper().startswith(_EXAMPLE_PREFIX):
            first_example_line = stripped[len(_EXAMPLE_PREFIX):].strip()
            if first_example_line:
                example_lines.append(first_example_line)
            in_example = True
        elif in_example and stripped:
            example_lines.append(stripped)

    if text is None:
        # Graceful fallback: no FACT: prefix — use the whole response
        text = raw.strip()

    example = "\n".join(example_lines) if example_lines else None
    # Return None only on empty text — example is always optional
    if not text:
        return None

    return Fact(topic="", text=text, example=example)
