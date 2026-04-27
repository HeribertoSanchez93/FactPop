from pathlib import Path

import pytest

import factpop.shared.storage.tinydb_factory as factory
from factpop.shared.storage.tinydb_factory import _TABLES


def test_init_db_creates_file(tmp_path: Path) -> None:
    db_path = tmp_path / "test.json"
    db = factory.init_db(path=db_path)

    assert db_path.exists(), "DB file must be created on disk"
    assert db is not None


def test_init_db_all_tables_accessible(tmp_path: Path) -> None:
    db = factory.init_db(path=tmp_path / "test.json")

    for table_name in _TABLES:
        table = db.table(table_name)
        assert table is not None, f"Table '{table_name}' must be accessible"


def test_init_db_returns_same_singleton(tmp_path: Path) -> None:
    db1 = factory.init_db(path=tmp_path / "test.json")
    db2 = factory.init_db(path=tmp_path / "test.json")

    assert db1 is db2, "init_db must return the same TinyDB instance (singleton)"


def test_get_db_raises_after_init(tmp_path: Path) -> None:
    factory.init_db(path=tmp_path / "test.json")
    db = factory.get_db()

    assert db is not None


def test_close_db_resets_singleton(tmp_path: Path) -> None:
    db1 = factory.init_db(path=tmp_path / "first.json")
    factory.close_db()

    db2 = factory.init_db(path=tmp_path / "second.json")
    assert db1 is not db2, "After close_db, init_db must return a fresh instance"


def test_close_db_idempotent() -> None:
    factory.close_db()
    factory.close_db()  # calling twice must not raise


def test_tables_survive_reopen(tmp_path: Path) -> None:
    db_path = tmp_path / "test.json"

    db = factory.init_db(path=db_path)
    db.table("topics").insert({"name": "Java", "active": True})
    factory.close_db()

    db = factory.init_db(path=db_path)
    rows = db.table("topics").all()
    assert len(rows) == 1
    assert rows[0]["name"] == "Java"
