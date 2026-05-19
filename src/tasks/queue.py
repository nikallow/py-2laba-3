import logging
from collections.abc import Iterator

from src.tasks.enums import TaskStatus
from src.tasks.task import Task, TaskSource
from src.tasks.validators import validate_priority

logger = logging.getLogger(__name__)


class TaskQueueIterator(Iterator[Task]):
    """
    Итератор очереди задач с ручным управлением состоянием обхода.
    """

    def __init__(self, sources: list[TaskSource]) -> None:
        """
        Инициализирует итератор списком источников задач.

        :param sources: Источники, которые нужно обойти.
        :type sources: list[TaskSource]
        """
        self._sources = sources
        self._source_index = 0
        self._current_tasks: Iterator[Task] | None = None
        self._current_source: TaskSource | None = None

    def __iter__(self) -> Iterator[Task]:
        """
        Возвращает текущий объект итератора.

        :rtype: Iterator[Task]
        """
        return self

    def __next__(self) -> Task:
        """
        Возвращает следующую задачу из текущего или следующего источника.

        Если источник завершился или вызвал исключение, итератор переходит к
        следующему зареганному источнику.

        :return: Следующая задача из очереди.
        :rtype: Task
        :raises StopIteration: Когда все источники полностью обойдены.
        """
        while self._source_index < len(self._sources):
            if self._current_tasks is None:
                self._start_next_source()
                continue

            try:
                return next(self._current_tasks)
            except StopIteration:
                self._finish_current_source()
            except Exception:
                logger.exception(
                    f"Unexpected failure in source "
                    f"{type(self._current_source).__name__}"
                )
                self._finish_current_source()

        raise StopIteration

    def _start_next_source(self) -> None:
        """
        Подготавливает итератор задач для следующего источника.
        """
        self._current_source = self._sources[self._source_index]

        try:
            self._current_tasks = iter(self._current_source.get_tasks())
        except Exception:
            logger.exception(
                f"Unexpected failure in source {type(self._current_source).__name__}"
            )
            self._finish_current_source()

    def _finish_current_source(self) -> None:
        """
        Завершает обработку текущего источника и сбрасывает его состояние.
        """
        self._source_index += 1
        self._current_tasks = None
        self._current_source = None


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
        Создает независимый итератор для обхода всех зарегистрированных источников.

        Каждый вызов iter возвращает новый объект итератора, поэтому
        очередь поддерживает повторный и независимый обход.

        :rtype: Iterator[Task]
        """
        return TaskQueueIterator(self._sources)

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
