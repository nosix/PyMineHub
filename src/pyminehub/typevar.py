from collections import namedtuple
from enum import Enum
from typing import TypeVar


T = TypeVar('T')  # Type

BT = TypeVar('BT')  # Base Type

NT = TypeVar('NT', int, float)  # Numeric Type

ET = TypeVar('ET', bound=Enum)  # Enum Type

TT = TypeVar('TT', bound=namedtuple)  # Tuple Type
