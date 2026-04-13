import logging
import sys
from itertools import islice
from pathlib import Path

from src.processor import TaskProcessor
from src.sources.api_src import APITaskSource
from src.sources.file_src import FileTaskSource
from src.sources.gen_src import RandomTaskGenerator
from src.tasks.enums import TaskStatus
from src.tasks.queue import TaskQueue

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()

    queue = TaskQueue()
    processor = TaskProcessor()

    queue.add_source(RandomTaskGenerator(count=10))
    queue.add_source(APITaskSource(endpoint="https://api.mock/tasks"))

    task_file = Path("tasks.txt")
    if not task_file.exists():
        task_file.write_text("Casino ДОДЕП\nGoose ", encoding="utf-8")
    queue.add_source(FileTaskSource(task_file))

    # Невалидный сурс
    queue.add_source(["goose", "casino"])

    new_tasks = list(queue.filter_by_status(TaskStatus.NEW))
    high_priority_preview = [
        task.summary for task in islice(queue.filter_higher_priority(2), 5)
    ]

    logger.info(f"New tasks count: {len(new_tasks)}")
    logger.info(f"Top high-priority preview: {high_priority_preview}")

    logger.info("Starting task processing")

    for task in queue:
        processor.process(task)

    logger.info("Processing completed")


if __name__ == "__main__":
    main()
