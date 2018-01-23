from enum import Enum


__all__ = [
    'PlayStatus',
    'ResourcePackStatus',
    'PlayerListType',
    'InventoryTransactionType'
]


class PlayStatus(Enum):
    LOGIN_SUCCESS = 0
    LOGIN_FAILED_CLIENT = 1
    LOGIN_FAILED_SERVER = 2
    PLAYER_SPAWN = 3
    LOGIN_FAILED_INVALID_TENANT = 4
    LOGIN_FAILED_VANILLA_EDU = 5
    LOGIN_FAILED_EDU_VANILLA = 6


class ResourcePackStatus(Enum):
    REFUSED = 1
    SEND_PACKS = 2
    HAVE_ALL_PACKS = 3
    COMPLETED = 4


class PlayerListType(Enum):
    ADD = 0
    REMOVE = 1


class InventoryTransactionType(Enum):
    NORMAL = 0
    MISMATCH = 1
    USE_ITEM = 2
    USE_ITEM_ON_ENTITY = 3
    RELEASE_ITEM = 4
