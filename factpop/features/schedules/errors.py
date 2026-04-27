from factpop.shared.errors import FactPopError


class InvalidTimeFormatError(FactPopError):
    """Raised when a time string is not valid HH:MM (24-hour, 00:00–23:59)."""


class TimeAlreadyExistsError(FactPopError):
    """Raised when the exact time is already in the configured schedule."""


class TimeNotFoundError(FactPopError):
    """Raised when a time to remove is not in the configured schedule."""
