from collections.abc import Iterator

import pytest
from _pytest.logging import LogCaptureFixture
from src.tasks.enums import TaskStatus
from src.tasks.exceptions import InvalidPriorityError, InvalidStatusError
from src.tasks.queue import TaskQueue
from src.tasks.task import Task


class ValidSource:
    def get_tasks(self) -> list[Task]:
        return [
            Task(
                task_id="1",
                description="new task",
                payload={"data": "test-1"},
                status=TaskStatus.NEW,
                priority=1,
            ),
            Task(
                task_id="2",
                description="ready task",
                payload={"data": "test-2"},
                status=TaskStatus.READY,
                priority=2,
            ),
            Task(
                task_id="3",
                description="done task",
                payload={"data": "test-3"},
                status=TaskStatus.DONE,
                priority=3,
            ),
        ]


class InvalidSource:
    pass


class BrokenSource:
    def get_tasks(self) -> None:
        raise RuntimeError("Goose!")


class BrokenDuringIterationSource:
    def get_tasks(self) -> Iterator[Task]:
        yield Task(
            task_id="broken-1",
            description="task before source failure",
            payload={"data": "broken"},
            status=TaskStatus.NEW,
            priority=1,
        )
        raise RuntimeError("Goose during iteration!")


def test_add_valid_source() -> None:
    queue = TaskQueue()
    source = ValidSource()

    assert queue.add_source(source) is True
    assert len(queue._sources) == 1


def test_add_invalid_source(caplog: LogCaptureFixture) -> None:
    queue = TaskQueue()
    source = InvalidSource()

    assert queue.add_source(source) is False
    assert "Contract violation" in caplog.text
    assert len(queue._sources) == 0


def test_iter_tasks_success() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    tasks = list(queue)
    assert len(tasks) == 3
    assert [task.id for task in tasks] == ["1", "2", "3"]
    assert tasks[0].status == TaskStatus.NEW
    assert tasks[1].status == TaskStatus.READY
    assert tasks[2].status == TaskStatus.DONE


def test_iter_tasks_handles_exception(caplog: LogCaptureFixture) -> None:
    queue = TaskQueue()

    queue.add_source(BrokenSource())
    queue.add_source(ValidSource())
    tasks = list(queue)

    assert "Unexpected failure in source" in caplog.text
    assert len(tasks) == 3
    assert tasks[0].id == "1"


def test_queue_supports_repeated_iteration() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == ["1", "2", "3"]
    assert second_pass == ["1", "2", "3"]


def test_queue_iter_returns_independent_iterator() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    first_iterator = iter(queue)
    second_iterator = iter(queue)

    assert first_iterator is not second_iterator
    assert iter(first_iterator) is first_iterator
    assert next(first_iterator).id == "1"
    assert next(first_iterator).id == "2"
    assert next(second_iterator).id == "1"


def test_iterator_raises_stop_iteration_after_last_task() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())
    iterator = iter(queue)

    assert next(iterator).id == "1"
    assert next(iterator).id == "2"
    assert next(iterator).id == "3"

    with pytest.raises(StopIteration):
        next(iterator)


def test_empty_queue_iterator_raises_stop_iteration() -> None:
    queue = TaskQueue()

    with pytest.raises(StopIteration):
        next(iter(queue))


def test_iter_tasks_handles_exception_during_iteration(
    caplog: LogCaptureFixture,
) -> None:
    queue = TaskQueue()

    queue.add_source(BrokenDuringIterationSource())
    queue.add_source(ValidSource())
    tasks = list(queue)

    assert "Unexpected failure in source" in caplog.text
    assert [task.id for task in tasks] == ["broken-1", "1", "2", "3"]


def test_filter_by_status_supports_string_value() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    tasks = list(queue.filter_by_status("READY"))

    assert len(tasks) == 1
    assert tasks[0].id == "2"
    assert tasks[0].status == TaskStatus.READY


def test_filter_by_status_raises_for_unsupported_status() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    with pytest.raises(InvalidStatusError, match="Unsupported status"):
        list(queue.filter_by_status("waiting"))


def test_filter_by_priority_returns_matching_tasks() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    tasks = list(queue.filter_by_priority(1))

    assert len(tasks) == 1
    assert tasks[0].id == "1"
    assert tasks[0].priority == 1


def test_filter_by_priority_rejects_invalid_priority_type() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    with pytest.raises(InvalidPriorityError, match="Priority must be an integer"):
        list(queue.filter_by_priority("1"))  # type: ignore[arg-type]


def test_filter_higher_priority_returns_up_to_threshold() -> None:
    queue = TaskQueue()
    queue.add_source(ValidSource())

    tasks = list(queue.filter_higher_priority(2))

    assert [task.id for task in tasks] == ["1", "2"]
    assert all(task.priority <= 2 for task in tasks)
