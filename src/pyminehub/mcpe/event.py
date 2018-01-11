from pyminehub.mcpe.value import *
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory


Event = ValueObject


class EventType(ValueType):
    PLAYER_LOGGED_IN = 0
    INVENTORY_LOADED = 1
    SLOT_INITIALIZED = 2
    FULL_CHUNK_LOADED = 3
    PLAYER_MOVED = 4
    BLOCK_UPDATED = 5
    ITEM_SPAWNED = 7
    ITEM_TAKEN = 8
    INVENTORY_UPDATED = 10
    ENTITY_REMOVED = 11
    EQUIPMENT_UPDATED = 12
    MOB_SPAWNED = 13


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
    EventType.INVENTORY_LOADED: [
        ('id', int),
        ('player_id', PlayerID),
        ('inventory', Tuple[Inventory, ...])
    ],
    EventType.SLOT_INITIALIZED: [
        ('id', int),
        ('player_id', PlayerID),
        ('inventory_slot', Optional[int]),
        ('hotbar_slot', int),
        ('equipped_item', Item)
    ],
    EventType.FULL_CHUNK_LOADED: [
        ('id', int),
        ('position', ChunkPosition),
        ('data', bytes)
    ],
    EventType.PLAYER_MOVED: [
        ('id', int),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('mode', MoveMode),
        ('on_ground', bool),
        ('riding_eid', EntityRuntimeID)
    ],
    EventType.BLOCK_UPDATED: [
        ('id', int),
        ('position', Vector3[int]),
        ('block_type', BlockType),
        ('block_aux', BlockData)
    ],
    EventType.ITEM_SPAWNED: [
        ('id', int),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('item', Item),
        ('position', Vector3[float]),
        ('motion', Vector3[float]),
        ('metadata', Tuple[EntityMetaData, ...])
    ],
    EventType.ITEM_TAKEN: [
        ('id', int),
        ('item_runtime_id', EntityRuntimeID),
        ('player_runtime_id', EntityRuntimeID)
    ],
    EventType.INVENTORY_UPDATED: [
        ('id', int),
        ('player_id', PlayerID),
        ('inventory_slot', int),
        ('slot', Item)
    ],
    EventType.ENTITY_REMOVED: [
        ('id', int),
        ('entity_runtime_id', EntityRuntimeID)
    ],
    EventType.EQUIPMENT_UPDATED: [
        ('id', int),
        ('entity_runtime_id', EntityRuntimeID),
        ('inventory_slot', Optional[int]),
        ('hotbar_slot', int),
        ('equipped_item', Item)
    ],
    EventType.MOB_SPAWNED: [
        ('id', int),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('type', EntityType),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('name', Optional[str])
    ]
}


event_factory = ValueObjectFactory(_event_specs)
