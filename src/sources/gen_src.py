from collections.abc import Iterable
from uuid import uuid4

from src.tasks.task import Task


class RandomTaskGenerator:
    def __init__(self, count: int = 5):
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        for _ in range(self.count):
            yield Task(
                id=str(uuid4()),
                payload={"source": "degenerator", "data": uuid4().hex[:16]},
            )
