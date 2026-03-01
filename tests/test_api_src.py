import logging
from unittest.mock import patch

from _pytest.logging import LogCaptureFixture
from src.sources.api_src import APITaskSource


def test_api_src_success() -> None:
    source = APITaskSource("https://fake.api/tasks")
    tasks = list(source.get_tasks())

    assert len(tasks) == 2
    assert tasks[0].id == "7281"
    assert tasks[0].payload["command"] == "get /users"
    assert tasks[0].payload["priority"] == "high"
    assert tasks[1].id == "7282"
    assert tasks[1].payload["command"] == "autoclean"
    assert tasks[1].payload["priority"] == "low"


def test_api_src_empty_response(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    with patch.object(APITaskSource, "_fetch_from_remote", return_value=[]):
        source = APITaskSource("https://fake.api/tasks")
        tasks = list(source.get_tasks())

        assert len(tasks) == 0
        assert "No tasks at this moment" in caplog.text


def test_api_src_missing_id(caplog: LogCaptureFixture) -> None:
    bad_data = [{"not_id": "123", "data": "casino"}]

    with patch.object(APITaskSource, "_fetch_from_remote", return_value=bad_data):
        source = APITaskSource("https://fake.api/tasks")
        tasks = list(source.get_tasks())

        assert len(tasks) == 0
        assert "Missing 'task_id'" in caplog.text


def test_api_src_critical_error(caplog: LogCaptureFixture) -> None:
    with patch.object(
        APITaskSource, "_fetch_from_remote", side_effect=Exception("Connection refused")
    ):
        source = APITaskSource("https://fake.api/tasks")
        tasks = list(source.get_tasks())

        assert len(tasks) == 0
        assert "Could not reach API" in caplog.text
