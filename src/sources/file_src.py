import logging
from collections.abc import Iterable
from pathlib import Path

from src.tasks.task import Task

logger = logging.getLogger(__name__)


class FileTaskSource:
    """
    Источник задач, читающий данные из текстового файла.

    Каждая непустая строка представляет собой одну задачу.

    :param file_path: Путь к файлу с данными задач.
    :type file_path: Path
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def get_tasks(self) -> Iterable[Task]:
        """
        Читает файл и генерирует объекты задач.

        :yields: Объект задачи, сформированный из строки файла.
        :rtype: Iterable[Task]
        """
        if not self.file_path.exists():
            logger.error(f"Source ignored: file not found at {self.file_path}")
            return

        if not self.file_path.is_file():
            logger.error(f"Source ignored: {self.file_path} is not a file")
            return

        try:
            with open(self.file_path, encoding="utf-8") as f:
                for i, raw_line in enumerate(f, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue

                    yield Task(
                        id=f"{self.file_path.name}-{i}",
                        payload={"source": f"file:{self.file_path}", "data": line},
                    )

        except PermissionError:
            logger.error(f"Permission denied: unable to read {self.file_path}")
        except UnicodeDecodeError:
            logger.error(f"Encoding error: {self.file_path} must be UTF-8 encoded")
        except OSError as e:
            logger.error(f"OS error occurred while reading {self.file_path}: {e}")
        except Exception:
            logger.exception(f"Unexpected failure in {self.file_path}")
