from typing import NamedTuple, Optional, Tuple
from uuid import UUID

from pyminehub.mcpe.command.const import CommandPermission, CommandOriginDataType

__all__ = [
    'CommandEnum',
    'CommandParameter',
    'CommandData',
    'CommandSpec',
    'CommandOriginData'
]


CommandEnum = NamedTuple('CommandEnum', [
    ('name', str),
    ('index', Tuple[int, ...])
])

CommandParameter = NamedTuple('CommandParameter', [
    ('name', str),
    ('type', int),
    ('is_optional', bool)
])

CommandData = NamedTuple('CommandData', [
    ('name', str),
    ('description', str),
    ('flags', int),
    ('permission', int),
    ('aliases', int),
    ('overloads', Tuple[Tuple[CommandParameter, ...], ...])
])

CommandSpec = NamedTuple('CommandSpec', [
    ('enum_values', Tuple[str, ...]),
    ('postfixes', Tuple[str, ...]),
    ('enums', Tuple[CommandEnum, ...]),
    ('command_data', Tuple[CommandData, ...]),
    ('permission', CommandPermission)
])

CommandOriginData = NamedTuple('CommandOriginData', [
    ('type', CommandOriginDataType),
    ('uuid', UUID),
    ('request_id', str),
    ('long1', Optional[int])
])
