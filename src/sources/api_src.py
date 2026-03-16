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

    PRIORITY_MAP = {"high": 1, "medium": 2, "low": 4}

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_tasks(self) -> Iterable[Task]:
        """
        Запрашивает задачи из API и возвращает итератор объектов Task.

        :return: Итератор задач.
        :rtype: Iterable[Task]
        """
        try:
            raw_data = self._fetch_from_remote()
            if not raw_data:
                logger.info("No tasks at this moment")
                return

            for item in raw_data:
                try:
                    if "id" not in item:
                        raise KeyError("Missing 'id' in API response")

                    task_data = item.copy()

                    task_id = task_data.pop("id")
                    description = task_data.pop("command", "No description provided")

                    # Маппим приоритет (по дефолту 3, если в API пришло что-то не то)
                    raw_priority = task_data.pop("priority", "medium")
                    priority = self.PRIORITY_MAP.get(raw_priority.lower(), 3)

                    yield Task(
                        task_id=task_id,
                        description=description,
                        priority=priority,
                        payload=task_data,
                    )

                except (KeyError, TypeError, ValueError) as e:
                    logger.error(f"Failed to parse task {item.get('task_id')}: {e}")
                    continue

        except Exception as e:
            logger.critical(f"Could not reach API at {self.endpoint}: {e}")

    @staticmethod
    def _fetch_from_remote() -> list[dict[str, Any]]:
        """
        Выполняет запрос к Mock API.

        :return: Список словарей с сырыми данными задач.
        :rtype: list[dict[str, Any]]
        """
        return [
            {"id": "7281", "command": "get /users", "priority": "high"},
            {"id": "7282", "command": "autoclean", "priority": "low"},
            {
                "id": "7283",
                "command": "backup",
                "priority": "medium",
                "extra": "daily",
            },
        ]
