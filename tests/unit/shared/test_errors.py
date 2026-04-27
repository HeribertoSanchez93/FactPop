import pytest

from factpop.shared.errors import FactPopError


def test_factpop_error_is_exception() -> None:
    assert issubclass(FactPopError, Exception)


def test_factpop_error_can_be_raised_and_caught() -> None:
    with pytest.raises(FactPopError, match="boom"):
        raise FactPopError("boom")
