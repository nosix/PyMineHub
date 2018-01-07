from enum import Enum
from typing import Iterator, Sequence, Type, Tuple


def _merge(enum_types: Sequence[Type[Enum]]) -> Iterator[Tuple[str, int]]:
    for enum_type in enum_types:
        for member in enum_type:
            yield member.name, member.value


def define_enum(name: str, *enum_types: Type[Enum]) -> Type[Enum]:
    """Define one Enum from multiple Enums.

    :param name: Enum class name
    :param enum_types: original Enums
    :return: joined Enum
    """
    # noinspection PyArgumentList
    return Enum(name, [member for member in _merge(enum_types)])
