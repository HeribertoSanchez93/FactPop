from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from platformdirs import user_log_dir

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    log_dir = Path(user_log_dir("FactPop"))
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "factpop.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s — %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
