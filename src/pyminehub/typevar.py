from enum import Enum
from typing import TypeVar


__all__ = ['T', 'BT', 'NT', 'ET']


T = TypeVar('T')  # Type

BT = TypeVar('BT')  # Base Type

NT = TypeVar('NT', int, float)  # Numeric Type

ET = TypeVar('ET', bound=Enum)  # Enum Type
