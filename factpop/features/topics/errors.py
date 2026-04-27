from factpop.shared.errors import FactPopError


class EmptyTopicNameError(FactPopError):
    """Raised when a topic name is empty or contains only whitespace."""


class DuplicateTopicError(FactPopError):
    """Raised when a topic with the same name (case-insensitive) already exists."""


class TopicNotFoundError(FactPopError):
    """Raised when a topic cannot be found by name or id."""
