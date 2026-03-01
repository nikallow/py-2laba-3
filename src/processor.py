from src.tasks.task import Task


class TaskProcessor:
    def process(self, task: Task) -> None:
        """
        Выполняет обработку задачи.

        :param task: Объект задачи, содержащий идентификатор и данные.
        :type task: Task
        :return: None
        """
        print(f"Processing task with id={task.id}")
        print(f"payload={task.payload}\n")
