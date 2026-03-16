import logging

from src.tasks.enums import TaskStatus
from src.tasks.task import Task

logger = logging.getLogger(__name__)


class TaskProcessor:
    def process(self, task: Task) -> None:
        """
        Выполняет обработку задачи с учетом её статуса.

        :param task: Объект задачи, содержащий идентификатор и данные.
        :type task: Task
        :return: None
        """
        if task.status == TaskStatus.NEW:
            task.ready()

        if task.status == TaskStatus.READY:
            task.start()

        if task.status != TaskStatus.IN_PROGRESS:
            logger.warning(
                "Task with id=%s cannot be processed in status=%s",
                task.id,
                task.status.value,
            )
            return

        logger.info("Processing task with id=%s", task.id)
        logger.info("Task id=%s was created %f sec ago", task.id, task.age_seconds)
        logger.debug(task.description)
        logger.debug("payload=%s", task.payload)

        task.complete()
