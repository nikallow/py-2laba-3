from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable

from src.tasks.descriptors import (
    CreatedAtDescriptor,
    ModelInfoDescriptor,
    NonEmptyString,
    PriorityDescriptor,
    StatusDescriptor,
)
from src.tasks.enums import TaskStatus
from src.tasks.exceptions import (
    InvalidDescriptionError,
    InvalidIDError,
    InvalidStatusTransitionError,
)


class Task:
    id = NonEmptyString(InvalidIDError, read_only=True)
    description = NonEmptyString(InvalidDescriptionError)
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    created_at = CreatedAtDescriptor()

    metadata = ModelInfoDescriptor()

    def __init__(
        self,
        task_id: str,
        description: str,
        payload: dict[str, Any] | None = None,
        priority: int = 3,
        status: TaskStatus = TaskStatus.NEW,
        created_at: datetime | None = None,
    ):
        """
        Инициализирует задачу.

        :param task_id: Уникальный идентификатор задачи.
        :type task_id: str
        :param description: Описание задачи.
        :type description: str
        :param payload: Дополнительные данные задачи.
        :type payload: dict[str, Any] | None
        :param priority: Приоритет задачи.
        :type priority: int
        :param status: Начальный статус задачи.
        :type status: TaskStatus | str
        :param created_at: Время создания задачи.
        :type created_at: datetime | None
        :return: None
        """
        self.id = task_id
        self.description = description
        self.payload = payload or {}
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now(UTC)

    @property
    def is_ready(self) -> bool:
        """
        Проверяет, готова ли задача к выполнению.

        :return: True, если задача находится в статусе READY, иначе False.
        :rtype: bool
        """
        return self.status == TaskStatus.READY

    @property
    def is_done(self) -> bool:
        """
        Проверяет, завершена ли задача.

        :return: True, если задача находится в статусе DONE, иначе False.
        :rtype: bool
        """
        return self.status == TaskStatus.DONE

    @property
    def age_seconds(self) -> float:
        """
        Возвращает возраст задачи в секундах.

        :return: Количество секунд с момента создания задачи.
        :rtype: float
        """

        return (datetime.now(UTC) - self.created_at).total_seconds()

    @property
    def summary(self) -> str:
        """
        Возвращает краткое текстовое представление задачи.

        :return: Строка с идентификатором, описанием и статусом задачи.
        :rtype: str
        """
        return f"[{self.id}] {self.description} ({self.status.value})"

    def ready(self) -> None:
        """
        Переводит задачу из статуса NEW в READY.

        :return: None
        :raises InvalidStatusTransitionError: Если текущий статус не NEW.
        """
        if self.status != TaskStatus.NEW:
            raise InvalidStatusTransitionError(
                "Only a task with status 'new' can be marked as ready."
            )
        self.status = TaskStatus.READY

    def start(self) -> None:
        """
        Переводит задачу из статуса READY в IN_PROGRESS.

        :return: None
        :raises InvalidStatusTransitionError: Если текущий статус не READY.
        """
        if self.status != TaskStatus.READY:
            raise InvalidStatusTransitionError(
                "Only a task with status 'ready' can be started."
            )
        self.status = TaskStatus.IN_PROGRESS

    def complete(self) -> None:
        """
        Переводит задачу из статуса IN_PROGRESS в DONE.

        :return: None
        :raises InvalidStatusTransitionError: Если текущий статус не IN_PROGRESS.
        """
        if self.status != TaskStatus.IN_PROGRESS:
            raise InvalidStatusTransitionError(
                "Only a task with status 'in_progress' can be completed."
            )
        self.status = TaskStatus.DONE

    def cancel(self) -> None:
        """
        Отменяет задачу.

        :return: None
        :raises InvalidStatusTransitionError: Если задача уже завершена.
        """
        if self.status == TaskStatus.DONE:
            raise InvalidStatusTransitionError("A completed task cannot be cancelled.")
        self.status = TaskStatus.CANCELLED

    def __repr__(self) -> str:
        """
        Возвращает строковое представление задачи для отладки.

        :return: Представление объекта Task.
        :rtype: str
        """
        return (
            "Task("
            f"id={self.id!r}, "
            f"description={self.description!r}, "
            f"priority={self.priority!r}, "
            f"status={self.status.value!r})"
        )


@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> Iterable[Task]: ...
