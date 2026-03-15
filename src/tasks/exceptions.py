class TaskError(Exception):
    ...


class TaskInvariantError(TaskError):
    ...


class InvalidID(TaskInvariantError):
    ...


class InvalidDescription(TaskInvariantError):
    ...


class InvalidPriority(TaskInvariantError):
    ...


class InvalidStatus(TaskInvariantError):
    ...


class InvalidStatusTransition(TaskInvariantError):
    ...


class InvalidTimestamp(TaskInvariantError):
    ...
