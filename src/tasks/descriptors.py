from datetime import datetime
from typing import cast

from src.tasks.enums import TaskStatus
from src.tasks.exceptions import (
    InvalidPriorityError,
    InvalidTimestampError,
    ReadOnlyFieldError,
    TaskInvariantError,
)


class NonEmptyString:
    """
    Data descriptor для непустой строки.

    Может использоваться как для обычного поля, так и для поля только для чтения.
    """

    def __init__(
            self,
            private_name: str,
            error_cls: type[TaskInvariantError],
            *,
            read_only: bool = False,
    ) -> None:
        """
        Инициализирует дескриптор строки.

        :param private_name: Имя внутреннего атрибута для хранения значения.
        :type private_name: str
        :param error_cls: Класс исключения для невалидного значения.
        :type error_cls: type[TaskInvariantError]
        :param read_only: Поле только для чтения.
        :type read_only: bool
        :return: None
        """
        self.private_name = private_name
        self.error_cls = error_cls
        self.read_only = read_only

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

    def __init__(self, private_name: str) -> None:
        """
        Инициализирует дескриптор приоритета.

        :param private_name: Имя внутреннего атрибута для хранения значения.
        :type private_name: str
        :return: None
        """
        self.private_name = private_name

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
        if not isinstance(value, int):
            raise InvalidPriorityError("Priority must be an integer.")
        if not 1 <= value <= 4:
            raise InvalidPriorityError("Priority must be between 1 and 4.")

        setattr(instance, self.private_name, value)


class StatusDescriptor:
    """
    Data descriptor для статуса задачи.
    """

    def __init__(self, private_name: str) -> None:
        """
        Инициализирует дескриптор статуса.

        :param private_name: Имя внутреннего атрибута для хранения значения.
        :type private_name: str
        :return: None
        """
        self.private_name = private_name

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

    def __init__(self, private_name: str) -> None:
        """
        Инициализирует дескриптор временной метки.

        :param private_name: Имя внутреннего атрибута для хранения значения.
        :type private_name: str
        :return: None
        """
        self.private_name = private_name

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
        :raises InvalidTimestampError: Если значение не является datetime.
        """
        if hasattr(instance, self.private_name):
            raise ReadOnlyFieldError("created_at is read-only")

        if not isinstance(value, datetime):
            raise InvalidTimestampError("created_at must be datetime.")

        setattr(instance, self.private_name, value)
