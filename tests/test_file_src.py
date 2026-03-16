from pathlib import Path
from unittest.mock import patch

from _pytest.logging import LogCaptureFixture
from src.sources.file_src import FileTaskSource


def test_get_tasks_success(tmp_path: Path) -> None:
    test_file = tmp_path / "task_src.txt"
    content = "task one \n\n task two "
    test_file.write_text(content, encoding="utf-8")

    source = FileTaskSource(test_file)
    tasks = list(source.get_tasks())

    assert len(tasks) == 2

    assert tasks[0].id == f"{test_file.name}-1"
    assert tasks[0].payload["source_file"] == str(test_file)
    assert tasks[0].payload["line_number"] == 1
    assert tasks[0].payload["raw_content"] == "task one"

    assert tasks[1].id == f"{test_file.name}-3"
    assert tasks[1].payload["source_file"] == str(test_file)
    assert tasks[1].payload["line_number"] == 3
    assert tasks[1].payload["raw_content"] == "task two"


def test_get_tasks_file_not_found(caplog: LogCaptureFixture) -> None:
    source = FileTaskSource(Path("not_existing_file.txt"))
    tasks = list(source.get_tasks())

    assert len(tasks) == 0
    assert "file not found" in caplog.text


def test_get_tasks_not_a_file(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    source = FileTaskSource(tmp_path)
    tasks = list(source.get_tasks())

    assert len(tasks) == 0
    assert "is not a file" in caplog.text


def test_get_tasks_permission_denied(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    test_file = tmp_path / "protected.txt"
    test_file.touch()

    source = FileTaskSource(test_file)
    with patch("builtins.open", side_effect=PermissionError):
        list(source.get_tasks())

    assert "Permission denied" in caplog.text


def test_get_tasks_unicode_error(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    test_file = tmp_path / "bad_encoding.txt"
    test_file.write_text("тест", encoding="cp1251")

    source = FileTaskSource(test_file)
    tasks = list(source.get_tasks())

    assert len(tasks) == 0
    assert "must be UTF-8 encoded" in caplog.text


def test_get_tasks_os_error(tmp_path: Path, caplog: LogCaptureFixture) -> None:
    test_file = tmp_path / "fail.txt"
    test_file.touch()

    source = FileTaskSource(test_file)
    with patch("builtins.open", side_effect=OSError("Disk error")):
        list(source.get_tasks())

    assert "OS error occurred while reading" in caplog.text
    assert "Disk error" in caplog.text
