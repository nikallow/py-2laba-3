from collections.abc import Iterable

from _pytest.logging import LogCaptureFixture
from src.tasks.enums import TaskStatus
from src.tasks.task import Task

from tasks.queue import TaskRegistry


class ValidSource:
    def get_tasks(self) -> Iterable[Task]:
        yield Task(
            task_id="1",
            description="test task",
            payload={"data": "test"},
            status=TaskStatus.NEW,
        )


class InvalidSource:
    pass


class BrokenSource:
    def get_tasks(self) -> None:
        raise RuntimeError("Goose!")


def test_add_valid_source() -> None:
    registry = TaskRegistry()
    source = ValidSource()

    assert registry.add_source(source) is True
    assert len(registry._sources) == 1


def test_add_invalid_source(caplog: LogCaptureFixture) -> None:
    registry = TaskRegistry()
    source = InvalidSource()

    assert registry.add_source(source) is False
    assert "Contract violation" in caplog.text
    assert len(registry._sources) == 0


def test_iter_tasks_success() -> None:
    registry = TaskRegistry()
    registry.add_source(ValidSource())

    tasks = list(registry.iter_tasks())
    assert len(tasks) == 1
    assert tasks[0].id == "1"
    assert tasks[0].description == "test task"
    assert tasks[0].status == TaskStatus.NEW


def test_iter_tasks_handles_exception(caplog: LogCaptureFixture) -> None:
    registry = TaskRegistry()

    registry.add_source(BrokenSource())
    registry.add_source(ValidSource())
    tasks = list(registry.iter_tasks())

    assert "Unexpected failure in source" in caplog.text

    assert len(tasks) == 1
    assert tasks[0].id == "1"
    assert tasks[0].status == TaskStatus.NEW
