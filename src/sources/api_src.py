import logging
from collections.abc import Iterable
from typing import Any

from src.tasks.task import Task

logger = logging.getLogger(__name__)


class APITaskSource:
    """
    Источник задач из API.

    :param endpoint: URL-адрес API для запроса задач.
    :type endpoint: str
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_tasks(self) -> Iterable[Task]:
        """
        Запрашивает задачи из API и возвращает итератор объектов Task.

        :return: Итератор задач.
        :rtype: Iterable[Task]
        """
        try:
            raw_data = APITaskSource._fetch_from_remote()
            if not raw_data:
                logger.info("No tasks at this moment")
                return

            for item in raw_data:
                try:
                    if "task_id" not in item:
                        raise KeyError("Missing 'task_id' in API response")

                    task_data = item.copy()
                    yield Task(id=task_data.pop("task_id"), payload=task_data)
                except (KeyError, TypeError) as e:
                    logger.error(f"Failed to parse task: {e}")
                    continue

        except Exception as e:
            logger.critical(f"Could not reach API at {self.endpoint}: {e}")

    @staticmethod
    def _fetch_from_remote() -> list[dict[str, Any]]:
        """
        Выполняет запрос к Mock API.

        :return: Список словарей с сырыми данными задач.
        :rtype: list[dict[str, typing.Any]]
        """
        return [
            {"task_id": "7281", "command": "get /users", "priority": "high"},
            {"task_id": "7282", "command": "autoclean", "priority": "low"},
        ]
