import uuid

from src.sources.gen_src import RandomTaskGenerator


def test_generator_count() -> None:
    count = 10
    source = RandomTaskGenerator(count=count)
    tasks = list(source.get_tasks())

    assert len(tasks) == count


def test_generator_uniqueness() -> None:
    source = RandomTaskGenerator(count=100)
    tasks = list(source.get_tasks())
    ids = [t.id for t in tasks]

    assert len(set(ids)) == 100


def test_generator_task_format() -> None:
    source = RandomTaskGenerator(count=1)
    task = next(iter(source.get_tasks()))

    assert task.id is not None
    assert uuid.UUID(task.id)
    assert task.description == "Generated task '1' for processing"
    assert task.payload["source"] == "degenerator"
    assert len(task.payload["data"]) == 16
