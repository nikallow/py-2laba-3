import logging
from collections.abc import Callable

import pytest
from _pytest.logging import LogCaptureFixture
from src.processor import TaskProcessor
from src.tasks.enums import TaskStatus
from src.tasks.task import Task


@pytest.fixture
def processor() -> TaskProcessor:
    return TaskProcessor()


@pytest.fixture
def task_factory() -> Callable[[TaskStatus], Task]:
    def _make_task(status: TaskStatus) -> Task:
        return Task(
            task_id="task-casino",
            description="process me",
            status=status,
            payload={"key": "value"},
        )

    return _make_task


@pytest.mark.parametrize(
    "initial_status", [TaskStatus.NEW, TaskStatus.READY, TaskStatus.IN_PROGRESS]
)
def test_processing_transitions_to_done(
        processor: TaskProcessor,
        task_factory: Callable[[TaskStatus], Task],
        caplog: LogCaptureFixture,
        initial_status: TaskStatus,
) -> None:
    caplog.set_level(logging.DEBUG)
    task = task_factory(initial_status)

    processor.process(task)

    assert task.status == TaskStatus.DONE
    assert f"Processing task with id={task.id}" in caplog.text


@pytest.mark.parametrize(
    "ignored_status", [TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.BLOCKED]
)
def test_processing_ignores_terminal_statuses(
        processor: TaskProcessor,
        task_factory: Callable[[TaskStatus], Task],
        caplog: LogCaptureFixture,
        ignored_status: TaskStatus,
) -> None:
    caplog.set_level(logging.WARNING)
    task = task_factory(ignored_status)

    processor.process(task)

    assert task.status == ignored_status
    assert f"cannot be processed in status={ignored_status.value}" in caplog.text
