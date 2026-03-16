from collections.abc import Iterable
from uuid import uuid4

from src.tasks.task import Task


class RandomTaskGenerator:
    def __init__(self, count: int = 5):
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for i in range(self.count):
            yield Task(
                task_id=str(uuid4()),
                description=f"Generated task '{i + 1}' for processing",
                payload={"source": "degenerator", "data": uuid4().hex[:16]},
            )
