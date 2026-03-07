import logging
import sys
from pathlib import Path

from src.processor import TaskProcessor
from src.registry import TaskRegistry
from src.sources.api_src import APITaskSource
from src.sources.file_src import FileTaskSource
from src.sources.gen_src import RandomTaskGenerator

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()

    registry = TaskRegistry()
    processor = TaskProcessor()

    registry.add_source(RandomTaskGenerator(count=10))
    registry.add_source(APITaskSource(endpoint="https://api.mock/tasks"))

    task_file = Path("tasks.txt")
    if not task_file.exists():
        task_file.write_text("Casino ДОДЕП\nGoose ", encoding="utf-8")
    registry.add_source(FileTaskSource(task_file))

    # Невалидный сурс
    registry.add_source(["goose", "casino"])

    logger.info("Starting task processing")

    for task in registry.iter_tasks():
        processor.process(task)

    logger.info("Processing completed")


if __name__ == "__main__":
    main()
