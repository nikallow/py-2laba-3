from datetime import datetime
from typing import Any, cast, overload

from src.tasks.enums import TaskStatus
from src.tasks.exceptions import (
    InvalidTimestampError,
    ReadOnlyFieldError,
    TaskInvariantError,
)
from src.tasks.validators import validate_priority


class ModelInfoDescriptor:
    """
    Non-data descriptor для предоставления информации о модели.

    (Демо для лабы): не имеет метода __set__.
    """

    def __get__(self, instance: object | None, owner: type[Any]) -> str:
        return f"TaskModel: {owner.__name__} (v2.0)"


class NonEmptyString:
    """
    Data descriptor для непустой строки.

    Может использоваться как для обычного поля, так и для поля только для чтения.
    """

    def __init__(
        self,
        error_cls: type[TaskInvariantError],
        *,
        read_only: bool = False,
    ) -> None:
        """
        Инициализирует дескриптор строки.

        :param error_cls: Класс исключения для невалидного значения.
        :type error_cls: type[TaskInvariantError]
        :param read_only: Поле только для чтения.
        :type read_only: bool
        :return: None
        """
        self.error_cls = error_cls
        self.read_only = read_only

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.private_name = f"_{name}"

    # For mypy
    @overload
    def __get__(self, instance: None, owner: type[Any]) -> NonEmptyString: ...

    @overload
    def __get__(self, instance: object, owner: type[Any]) -> str: ...

    def __get__(
        self, instance: object, owner: type | None = None
    ) -> str | NonEmptyString:
        """
        Возвращает значение строкового атрибута.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param owner: Класс владельца.
        :type owner: type | None
        :return: Значение атрибута или сам дескриптор при доступе через класс.
        :rtype: str | NonEmptyString
        """
        if instance is None:
            return self
        return cast(str, getattr(instance, self.private_name))

    def __set__(self, instance: object, value: str) -> None:
        """
        Устанавливает значение строкового атрибута с валидацией.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param value: Новое значение атрибута.
        :type value: str
        :return: None
        :raises ReadOnlyFieldError: Если поле только для чтения и уже инициализировано.
        :raises TaskInvariantError: Если строка пустая или имеет неверный тип.
        """
        if self.read_only and hasattr(instance, self.private_name):
            raise ReadOnlyFieldError(f"{self.private_name} is read-only.")

        if not isinstance(value, str) or not value.strip():
            raise self.error_cls(f"{self.private_name} must be a non-empty string.")

        setattr(instance, self.private_name, value.strip())


class PriorityDescriptor:
    """
    Data descriptor для приоритета задачи.
    """

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> PriorityDescriptor: ...

    @overload
    def __get__(self, instance: object, owner: type[Any]) -> int: ...

    def __get__(
        self, instance: object, owner: type | None = None
    ) -> int | PriorityDescriptor:
        """
        Возвращает значение приоритета.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param owner: Класс владельца.
        :type owner: type | None
        :return: Значение приоритета или сам дескриптор при доступе через класс.
        :rtype: int | PriorityDescriptor
        """
        if instance is None:
            return self
        return cast(int, getattr(instance, self.private_name))

    def __set__(self, instance: object, value: int) -> None:
        """
        Устанавливает значение приоритета с валидацией.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param value: Новое значение приоритета.
        :type value: int
        :return: None
        :raises InvalidPriorityError: Если значение не является целым числом
            или не входит в допустимый диапазон.
        """
        setattr(instance, self.private_name, validate_priority(value))


class StatusDescriptor:
    """
    Data descriptor для статуса задачи.
    """

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> StatusDescriptor: ...

    @overload
    def __get__(self, instance: object, owner: type[Any]) -> TaskStatus: ...

    def __get__(
        self,
        instance: object,
        owner: type | None = None,
    ) -> TaskStatus | StatusDescriptor:
        """
        Возвращает статус задачи.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param owner: Класс владельца.
        :type owner: type | None
        :return: Текущий статус или сам дескриптор при доступе через класс.
        :rtype: TaskStatus | StatusDescriptor
        """
        if instance is None:
            return self
        return cast(TaskStatus, getattr(instance, self.private_name))

    def __set__(self, instance: object, value: TaskStatus | str) -> None:
        """
        Устанавливает статус задачи с нормализацией.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param value: Новый статус в виде строки или TaskStatus.
        :type value: TaskStatus | str
        :return: None
        """
        setattr(instance, self.private_name, TaskStatus.from_value(value))


class CreatedAtDescriptor:
    """
    Data descriptor для времени создания задачи.

    Поле является только для чтения после первой инициализации.
    """

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> CreatedAtDescriptor: ...

    @overload
    def __get__(self, instance: object, owner: type[Any]) -> datetime: ...

    def __get__(
        self,
        instance: object,
        owner: type | None = None,
    ) -> datetime | CreatedAtDescriptor:
        """
        Возвращает время создания задачи.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param owner: Класс владельца.
        :type owner: type | None
        :return: Время создания или сам дескриптор при доступе через класс.
        :rtype: datetime | CreatedAtDescriptor
        """
        if instance is None:
            return self
        return cast(datetime, getattr(instance, self.private_name))

    def __set__(self, instance: object, value: datetime) -> None:
        """
        Устанавливает время создания задачи.

        :param instance: Экземпляр объекта.
        :type instance: object
        :param value: Время создания.
        :type value: datetime
        :return: None
        :raises ReadOnlyFieldError: Если поле уже было инициализировано.
        :raises InvalidTimestampError: Если значение не является datetime
            или не установлена таймзона.
        """
        if hasattr(instance, self.private_name):
            raise ReadOnlyFieldError("created_at is read-only.")

        if not isinstance(value, datetime):
            raise InvalidTimestampError("created_at must be datetime.")

        if value.tzinfo is None:
            raise InvalidTimestampError("created_at must use UTC tz.")

        setattr(instance, self.private_name, value)
