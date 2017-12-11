from enum import Enum


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


class Dimension(Enum):
    OVERWORLD = 0
    NETHER = 1
    THE_END = 2

    
class Generator(Enum):
    OLD = 0
    INFINITE = 1
    FLAT = 2


class GameMode(Enum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2


class Difficulty(Enum):
    PEACEFUL = 0
    EASY = 1
    NORMAL = 2
    HARD = 3

    
class GameRuleType(Enum):
    BOOL = 1
    INT = 2
    FLOAT = 3


class PlayerPermission(Enum):
    CUSTOM = 3
    OPERATOR = 2
    MEMBER = 1
    VISITOR = 0


class MetaDataType(Enum):
    BYTE = 0
    SHORT = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    SLOT = 5
    INT_VECTOR3 = 6
    LONG = 7
    FLOAT_VECTOR3 = 8


class PlayerListType(Enum):
    ADD = 0
    REMOVE = 1


class RecipeType(Enum):
    SHAPELESS = 0
    SHAPED = 1
    FURNACE = 2
    FURNACE_DATA = 3
    MULTI = 4
    SHULKER_BOX = 5
