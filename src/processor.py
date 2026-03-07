import logging

from src.tasks.task import Task

logger = logging.getLogger(__name__)


class TaskProcessor:
    def process(self, task: Task) -> None:
        """
        Выполняет обработку задачи.

        :param task: Объект задачи, содержащий идентификатор и данные.
        :type task: Task
        :return: None
        """
        logger.info("Processing task with id=%s", task.id)
        logger.debug("payload=%s", task.payload)
