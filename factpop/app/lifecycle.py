from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from filelock import FileLock, Timeout
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


def _lock_path() -> Path:
    data_dir = Path(user_data_dir("FactPop"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "factpop.lock"


@contextmanager
def instance_lock() -> Generator[None, None, None]:
    """Ensure only one FactPop process runs at a time.

    Exits with code 1 if another instance already holds the lock.
    """
    lock = FileLock(str(_lock_path()), timeout=0)
    try:
        lock.acquire(timeout=0)
    except Timeout:
        print(
            "FactPop is already running. Only one instance is allowed.",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info("FactPop instance started (lock acquired at %s)", _lock_path())
    try:
        yield
    finally:
        lock.release()
        logger.info("FactPop instance stopped (lock released)")
