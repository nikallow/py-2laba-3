from datetime import UTC, datetime, timedelta

import pytest
from src.tasks.descriptors import (
    CreatedAtDescriptor,
    ModelInfoDescriptor,
    NonEmptyString,
    PriorityDescriptor,
    StatusDescriptor,
)
from src.tasks.enums import TaskStatus
from src.tasks.exceptions import (
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidTimestampError,
    ReadOnlyFieldError,
)


class DummyModel:
    metadata = ModelInfoDescriptor()
    description = NonEmptyString(InvalidDescriptionError)
    id = NonEmptyString(InvalidDescriptionError, read_only=True)
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    created_at = CreatedAtDescriptor()


class TestModelInfoDescriptor:
    def test_get_from_class(self) -> None:
        assert DummyModel.metadata == "TaskModel: DummyModel (v2.0)"

    def test_get_from_instance(self) -> None:
        obj = DummyModel()
        assert obj.metadata == "TaskModel: DummyModel (v2.0)"

    def test_is_non_data_descriptor(self) -> None:
        obj = DummyModel()
        obj.metadata = "Custom runtime info"
        assert obj.metadata == "Custom runtime info"
        assert DummyModel.metadata == "TaskModel: DummyModel (v2.0)"


class TestNonEmptyString:
    def test_set_valid_string(self) -> None:
        obj = DummyModel()
        obj.description = "  Initial Description  "
        assert obj.description == "Initial Description"

    def test_set_empty_description_raises_error(self) -> None:
        obj = DummyModel()
        with pytest.raises(InvalidDescriptionError, match="must be a non-empty string"):
            obj.description = "   "

    def test_set_non_string_raises_error(self) -> None:
        obj = DummyModel()
        with pytest.raises(InvalidDescriptionError):
            obj.description = 12345  # type: ignore[assignment]

    def test_read_only_id_field_raises_error_on_reassign(self) -> None:
        obj = DummyModel()
        obj.id = "task-1"
        assert obj.id == "task-1"
        with pytest.raises(ReadOnlyFieldError, match="is read-only"):
            obj.id = "new-id-456"

    def test_descriptor_access_via_class(self) -> None:
        assert isinstance(DummyModel.id, NonEmptyString)
        assert isinstance(DummyModel.description, NonEmptyString)


class TestPriorityDescriptor:
    @pytest.mark.parametrize("valid_priority", [1, 2, 3, 4])
    def test_set_valid_priority(self, valid_priority: int) -> None:
        obj = DummyModel()
        obj.priority = valid_priority
        assert obj.priority == valid_priority

    @pytest.mark.parametrize("invalid_priority", [0, 5, -1])
    def test_set_out_of_range_priority_raises_error(
        self, invalid_priority: int
    ) -> None:
        obj = DummyModel()
        with pytest.raises(
            InvalidPriorityError, match="Priority must be between 1 and 4"
        ):
            obj.priority = invalid_priority

    def test_set_non_integer_priority_raises_error(self) -> None:
        obj = DummyModel()
        with pytest.raises(InvalidPriorityError, match="Priority must be an integer"):
            obj.priority = "2"  # type: ignore[assignment]


class TestStatusDescriptor:
    def test_set_status_from_enum(self) -> None:
        obj = DummyModel()
        obj.status = TaskStatus.IN_PROGRESS
        assert obj.status == TaskStatus.IN_PROGRESS

    def test_descriptor_access_via_class(self) -> None:
        assert isinstance(DummyModel.status, StatusDescriptor)


class TestCreatedAtDescriptor:
    def test_rejects_reassignment(self) -> None:
        obj = DummyModel()
        obj.created_at = datetime.now(UTC)
        new_time = datetime.now(UTC) + timedelta(seconds=10)
        with pytest.raises(ReadOnlyFieldError, match="created_at is read-only"):
            obj.created_at = new_time

    def test_rejects_datetime_without_tz_on_set(self) -> None:
        obj = DummyModel()
        with pytest.raises(InvalidTimestampError, match="created_at must use UTC tz"):
            obj.created_at = datetime.now()

    def test_rejects_non_datetime_value(self) -> None:
        obj = DummyModel()
        with pytest.raises(InvalidTimestampError, match="created_at must be datetime"):
            obj.created_at = "2026-04-01T00:00:00"  # type: ignore[assignment]
