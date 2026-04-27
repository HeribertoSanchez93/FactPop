import logging
import logging.handlers
from pathlib import Path
from unittest.mock import patch

import pytest

from factpop.shared.logging_config import setup_logging


@pytest.fixture(autouse=True)
def reset_root_logger():
    """Remove handlers added by setup_logging so tests don't bleed into each other."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    yield
    root.handlers = original_handlers
    root.setLevel(original_level)


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "factpop.log"

    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    assert log_file.exists(), "Log file must be created on disk"


def test_setup_logging_adds_rotating_file_handler(tmp_path: Path) -> None:
    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    root = logging.getLogger()
    file_handlers = [
        h for h in root.handlers
        if isinstance(h, logging.handlers.RotatingFileHandler)
    ]
    assert len(file_handlers) >= 1, "At least one RotatingFileHandler must be attached"


def test_setup_logging_adds_console_handler(tmp_path: Path) -> None:
    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    root = logging.getLogger()
    stream_handlers = [
        h for h in root.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.handlers.RotatingFileHandler)
    ]
    assert len(stream_handlers) >= 1, "At least one StreamHandler must be attached"


def test_setup_logging_respects_level(tmp_path: Path) -> None:
    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging(level=logging.DEBUG)

    assert logging.getLogger().level == logging.DEBUG


def test_log_message_written_to_file(tmp_path: Path) -> None:
    log_file = tmp_path / "factpop.log"

    with patch("factpop.shared.logging_config.user_log_dir", return_value=str(tmp_path)):
        setup_logging()

    logging.getLogger("factpop.test").info("stage1-sentinel")

    content = log_file.read_text(encoding="utf-8")
    assert "stage1-sentinel" in content
