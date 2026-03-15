from enum import Enum
from typing import Any

from src.tasks.exceptions import InvalidStatus


class TaskStatus(str, Enum):
    NEW = "new"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

    @classmethod
    def from_value(cls, value: Any) -> TaskStatus:
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value.lower())
            except ValueError as e:
                raise InvalidStatus(f"Unsupported status: {value!r}") from e

        raise InvalidStatus(f"Unsupported status type: {type(value).__name__}")
