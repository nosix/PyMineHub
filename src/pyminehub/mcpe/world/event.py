from pyminehub.mcpe.value import *
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory


Event = ValueObject


class EventType(ValueType):
    PLAYER_LOGGED_IN = 0
    UNKNOWN1 = 1
    UNKNOWN2 = 2
    FULL_CHUNK_LOADED = 3


_event_specs = {
    EventType.PLAYER_LOGGED_IN: [
        ('id', int),
        ('player_id', PlayerID),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('game_mode', GameMode),
        ('position', Vector3),
        ('pitch', float),
        ('yaw', float),
        ('spawn', Vector3),
        ('permission', PlayerPermission),
        ('attributes', Tuple[Attribute, ...])
    ],
    EventType.UNKNOWN1: [
        ('id', int),
        ('player_id', PlayerID),
        ('entity_data', Tuple[EntityMetaData, ...]),
        ('inventory', Tuple[Inventory, ...])
    ],
    EventType.UNKNOWN2: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    EventType.FULL_CHUNK_LOADED: [
        ('id', int),
        ('position', ChunkPosition),
        ('data', bytes)
    ]
}


event_factory = ValueObjectFactory(_event_specs)
