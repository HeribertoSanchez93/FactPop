import pytest
import factpop.shared.storage.tinydb_factory as db_module


@pytest.fixture(autouse=True)
def reset_db_singleton():
    """Reset the TinyDB singleton before and after every test."""
    db_module.close_db()
    yield
    db_module.close_db()
