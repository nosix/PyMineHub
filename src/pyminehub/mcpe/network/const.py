from enum import Enum


__all__ = [
    'GUEST_XUID',
    'PlayStatus',
    'ResourcePackStatus',
    'PlayerListType',
    'InventoryTransactionType',
    'UseItemActionType',
    'UseItemOnEntityActionType',
    'ReleaseItemActionType',
]


GUEST_XUID = ':GUEST:'


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


class UseItemActionType(Enum):
    CLICK_BLOCK = 0
    CLICK_AIR = 1
    BREAK_BLOCK = 2


class UseItemOnEntityActionType(Enum):
    INTERACT = 0
    ATTACK = 1


class ReleaseItemActionType(Enum):
    RELEASE = 0  # bow shoot
    CONSUME = 1  # eat food, drink potion
