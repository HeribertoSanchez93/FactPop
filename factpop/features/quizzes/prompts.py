from __future__ import annotations

from factpop.features.quizzes.models import Quiz
from factpop.features.history.models import FactRecord

_OPTION_LETTERS = ("A", "B", "C", "D")


def build_quiz_prompt(source_fact_text: str) -> str:
    """Build a prompt for MCQ generation grounded exclusively in the source fact."""
    return (
        f"You are a quiz generator. Based ONLY on the following fact, generate a "
        f"multiple-choice question with exactly 4 answer options.\n\n"
        f"SOURCE FACT:\n{source_fact_text}\n\n"
        f"Rules:\n"
        f"- The question MUST be answerable using ONLY the information in the source fact.\n"
        f"- Do NOT introduce any information not present in the source fact.\n"
        f"- Provide exactly 4 options labeled A, B, C, D.\n"
        f"- One option is correct; the other three are plausible distractors.\n\n"
        f"Respond ONLY in this exact format:\n"
        f"QUESTION: <your question>\n"
        f"A: <option A>\n"
        f"B: <option B>\n"
        f"C: <option C>\n"
        f"D: <option D>\n"
        f"CORRECT: <A, B, C, or D>"
    )


def parse_quiz_response(raw: str, source_fact_text: str) -> Quiz | None:
    """Parse an LLM response into a Quiz with 4 options and a correct index."""
    if not raw or not raw.strip():
        return None

    question: str | None = None
    options: list[str] = []
    correct_letter: str | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        upper = stripped.upper()

        if upper.startswith("QUESTION:"):
            question = stripped[len("QUESTION:"):].strip()
        elif upper.startswith("CORRECT:"):
            correct_letter = stripped[len("CORRECT:"):].strip().upper()
        else:
            for letter in _OPTION_LETTERS:
                if upper.startswith(f"{letter}:"):
                    options.append(stripped[2:].strip())
                    break

    if question is None or len(options) != 4 or correct_letter not in _OPTION_LETTERS:
        return None

    correct_index = _OPTION_LETTERS.index(correct_letter)

    # Construct a minimal FactRecord placeholder (topic set by caller)
    placeholder = FactRecord(id="", topic="", text=source_fact_text, shown_at="")
    return Quiz(
        source_fact=placeholder,
        question=question,
        options=options,
        correct_index=correct_index,
    )
