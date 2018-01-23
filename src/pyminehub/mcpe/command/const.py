from enum import Enum


__all__ = [
    'CommandPermission',
    'CommandArgType',
    'CommandOriginDataType'
]


class CommandPermission(Enum):
    NORMAL = 0
    OPERATOR = 1
    HOST = 2
    AUTOMATION = 3
    ADMIN = 4


class CommandArgType(Enum):
    INT = 1
    FLOAT = 2
    VALUE = 3
    TARGET = 4
    STRING = 13
    POSITION = 14
    MESSAGE = 17
    TEXT = 19
    JSON = 22
    COMMAND = 29


class CommandOriginDataType(Enum):
    PLAYER = 0
    BLOCK = 1
    MINECART_BLOCK = 2
    DEV_CONSOLE = 3
    TEST = 4
    AUTOMATION_PLAYER = 5
    CLIENT_AUTOMATION = 6
    DEDICATED_SERVER = 7
    ENTITY = 8
    VIRTUAL = 9
    GAME_ARGUMENT = 10
    ENTITY_SERVER = 11
