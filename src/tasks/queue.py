import logging
from collections.abc import Iterator

from src.tasks.enums import TaskStatus
from src.tasks.task import Task, TaskSource
from src.tasks.validators import validate_priority

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    Очередь задач, объединяющая несколько источников.
    """

    def __init__(self) -> None:
        self._sources: list[TaskSource] = []

    def add_source(self, source: object) -> bool:
        """
        Регистрирует новый источник задач в системе.

        Использует runtime-проверку протокола (Duck Typing) для валидации источника.

        :param source: Объект, который должен реализовать метод ``get_tasks()``.
        :type source: object
        :return: True, если источник соответствует контракту и добавлен, иначе False.
        :rtype: bool
        """
        if isinstance(source, TaskSource):
            self._sources.append(source)
            return True
        logger.error(
            f"Contract violation: '{type(source).__name__}' is not a TaskSource."
        )
        return False

    def __iter__(self) -> Iterator[Task]:
        """
        Последовательно запрашивает задачи из всех зарегистрированных источников.

        Метод устойчив к ошибкам отдельных источников: если один источник
        вызывает исключение, итерация продолжается для остальных.

        :yield: Объект задачи, полученный из одного из источников.
        :rtype: Iterator[Task]
        """
        for source in self._sources:
            try:
                yield from source.get_tasks()
            except Exception:
                logger.exception(
                    f"Unexpected failure in source {type(source).__name__}"
                )

    def filter_by_status(self, status: TaskStatus | str) -> Iterator[Task]:
        """
        Лениво фильтрует задачи по статусу.

        :param status: Статус задачи.
        :type status: TaskStatus | str
        :yield: Задачи с указанным статусом.
        :rtype: Iterator[Task]
        """
        status = TaskStatus.from_value(status)

        for task in self:
            if task.status == status:
                yield task

    def filter_by_priority(self, priority: int) -> Iterator[Task]:
        """
        Лениво фильтрует задачи по приоритету.

        :param priority: Значение приоритета задачи.
        :type priority: int
        :yield: Задачи с указанным приоритетом.
        :rtype: Iterator[Task]
        """
        priority = validate_priority(priority)

        for task in self:
            if task.priority == priority:
                yield task

    def filter_higher_priority(self, priority: int) -> Iterator[Task]:
        """
        Лениво отбирает задачи с приоритетом выше или равным указанному.
        Меньшее числовое значение соответствует более высокому приоритету.

        :param priority: Пороговое значение приоритета.
        :type priority: int
        :yield: Задачи с приоритетом выше или равным указанному.
        :rtype: Iterator[Task]
        """
        priority = validate_priority(priority)

        for task in self:
            if task.priority <= priority:
                yield task
