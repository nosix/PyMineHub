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
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('spawn', Vector3[int]),
        ('bed_position', Vector3[int]),
        ('permission', PlayerPermission),
        ('attributes', Tuple[Attribute, ...]),
        ('metadata_flags', EntityMetaDataFlagValue)
    ],
    EventType.UNKNOWN1: [
        ('id', int),
        ('player_id', PlayerID),
        ('inventory', Tuple[Inventory, ...])
    ],
    EventType.UNKNOWN2: [
        ('id', int),
        ('player_id', PlayerID),
        ('equipped_item', Slot),
        ('inventory_slot', int),
        ('hotbar_slot', int)
    ],
    EventType.FULL_CHUNK_LOADED: [
        ('id', int),
        ('position', ChunkPosition),
        ('data', bytes)
    ]
}


event_factory = ValueObjectFactory(_event_specs)
