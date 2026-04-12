from typing import Any

from src.tasks.exceptions import InvalidPriorityError


def validate_priority(value: Any) -> int:
    """
    Валидирует значение приоритета задачи.

    :param value: Значение приоритета.
    :type value: Any
    :return: Корректный числовой приоритет.
    :rtype: int
    :raises InvalidPriorityError: Если значение не является целым числом
        или не входит в диапазон от 1 до 4.
    """
    if not isinstance(value, int):
        raise InvalidPriorityError("Priority must be an integer.")
    if not 1 <= value <= 4:
        raise InvalidPriorityError("Priority must be between 1 and 4.")
    return value
