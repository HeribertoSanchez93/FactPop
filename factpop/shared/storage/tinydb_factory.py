from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir
from tinydb import TinyDB

_TABLES = ("topics", "app_config", "fact_history", "quiz_attempts", "review_queue")

_db: TinyDB | None = None


def _data_path() -> Path:
    data_dir = Path(user_data_dir("FactPop"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "factpop.json"


def get_db() -> TinyDB:
    global _db
    if _db is None:
        _db = TinyDB(str(_data_path()))
    return _db


def init_db(path: Path | None = None) -> TinyDB:
    """Initialize the TinyDB singleton and ensure all tables exist.

    Args:
        path: Override the DB file path (used in tests via tmp_path).
    """
    global _db
    if _db is None:
        resolved = path if path is not None else _data_path()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        _db = TinyDB(str(resolved))
    for table_name in _TABLES:
        _db.table(table_name)
    return _db


def close_db() -> None:
    global _db
    if _db is not None:
        _db.close()
        _db = None
