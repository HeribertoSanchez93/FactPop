"""Automated tests for the notification dispatcher layer.

TkPopupDispatcher, plyer_toast, and pystray tray are GUI/OS components
that cannot be meaningfully automated — those are covered in tests/manual-qa.md.

These tests cover:
  - NullDispatcher: records calls and stores callbacks (used by all other tests)
  - truncate_for_toast: toast truncation utility
  - Callback wiring: on_save and on_show_another execute the right logic
"""
from factpop.features.history.models import FactRecord
from factpop.features.notifications.null import NullDispatcher
from factpop.features.notifications.utils import truncate_for_toast


def _make_record(topic: str = "Java", text: str = "Java uses the JVM.") -> FactRecord:
    return FactRecord(id="test-1", topic=topic, text=text, shown_at="2026-04-25T10:00:00")


# --- NullDispatcher ---

def test_null_dispatcher_records_shown_fact() -> None:
    disp = NullDispatcher()
    record = _make_record()
    disp.show_fact(record, on_save=lambda: None, on_show_another=lambda: None)
    assert disp.shown_count == 1


def test_null_dispatcher_stores_last_record() -> None:
    disp = NullDispatcher()
    record = _make_record()
    disp.show_fact(record, on_save=lambda: None, on_show_another=lambda: None)
    assert disp.last_record is record


def test_null_dispatcher_accumulates_shown_count() -> None:
    disp = NullDispatcher()
    for i in range(3):
        disp.show_fact(_make_record(text=f"fact {i}"), on_save=lambda: None, on_show_another=lambda: None)
    assert disp.shown_count == 3


def test_null_dispatcher_trigger_save_executes_callback() -> None:
    disp = NullDispatcher()
    saved = []
    disp.show_fact(_make_record(), on_save=lambda: saved.append(True), on_show_another=lambda: None)
    disp.trigger_save()
    assert saved == [True]


def test_null_dispatcher_trigger_show_another_executes_callback() -> None:
    disp = NullDispatcher()
    called = []
    disp.show_fact(_make_record(), on_save=lambda: None, on_show_another=lambda: called.append(True))
    disp.trigger_show_another()
    assert called == [True]


def test_null_dispatcher_trigger_close_does_not_call_save_or_show_another() -> None:
    disp = NullDispatcher()
    save_calls = []
    show_another_calls = []
    disp.show_fact(
        _make_record(),
        on_save=lambda: save_calls.append(True),
        on_show_another=lambda: show_another_calls.append(True),
    )
    disp.trigger_close()
    assert save_calls == []
    assert show_another_calls == []


def test_null_dispatcher_trigger_save_only_fires_last_registered_callback() -> None:
    disp = NullDispatcher()
    first_calls = []
    second_calls = []
    disp.show_fact(_make_record(), on_save=lambda: first_calls.append(1), on_show_another=lambda: None)
    disp.show_fact(_make_record(), on_save=lambda: second_calls.append(2), on_show_another=lambda: None)
    disp.trigger_save()
    assert first_calls == []  # overwritten by second call
    assert second_calls == [2]


def test_null_dispatcher_initially_has_no_shown_facts() -> None:
    disp = NullDispatcher()
    assert disp.shown_count == 0
    assert disp.last_record is None


# --- truncate_for_toast ---

def test_truncate_short_text_unchanged() -> None:
    text = "Java uses the JVM."
    assert truncate_for_toast(text) == text


def test_truncate_exact_100_chars_unchanged() -> None:
    text = "a" * 100
    assert truncate_for_toast(text) == text


def test_truncate_over_100_chars_adds_ellipsis() -> None:
    text = "a" * 110
    result = truncate_for_toast(text)
    assert len(result) == 100
    assert result.endswith("...")


def test_truncate_over_100_preserves_start() -> None:
    text = "Java uses the JVM. " + "x" * 100
    result = truncate_for_toast(text)
    assert result.startswith("Java uses the JVM.")


def test_truncate_custom_max_length() -> None:
    text = "Hello World"
    result = truncate_for_toast(text, max_chars=5)
    assert len(result) == 5
    assert result == "He..."


def test_truncate_empty_string_unchanged() -> None:
    assert truncate_for_toast("") == ""
