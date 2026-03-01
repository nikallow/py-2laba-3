import logging
from collections.abc import Iterable
from typing import Any

from src.tasks.task import Task, TaskSource

logger = logging.getLogger(__name__)


class TaskRegistry:
    """
    Регистри сурцов
    """

    def __init__(self) -> None:
        self._sources: list[TaskSource] = []

    def add_source(self, source: Any) -> bool:
        """
        Регистрирует новый источник задач в системе.

        Использует runtime-проверку протокола (Duck Typing) для валидации источника.

        :param source: Объект, который должен реализовать метод ``get_tasks()``.
        :type source: Any
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

    def iter_tasks(self) -> Iterable[Task]:
        """
        Последовательно запрашивает задачи из всех зарегистрированных источников.

        Метод устойчив к ошибкам отдельных источников: если один источник
        вызывает исключение, итерация продолжается для остальных.

        :yield: Объект задачи, полученный из одного из источников.
        :rtype: Iterable[Task]
        """
        for source in self._sources:
            try:
                yield from source.get_tasks()
            except Exception:
                logger.exception(
                    f"Unexpected failure in source {type(source).__name__}"
                )
