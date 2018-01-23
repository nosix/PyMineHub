from typing import Optional, Tuple

from pyminehub.mcpe.const import GameMode, PlayerPermission, MoveMode, EntityType
from pyminehub.mcpe.geometry import Vector3, ChunkPosition
from pyminehub.mcpe.value import *
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

__all__ = [
    'Event',
    'EventType',
    'event_factory'
]


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
    MOB_MOVED = 14
    ENTITY_LOADED = 15


_event_specs = {
    EventType.PLAYER_LOGGED_IN: [
        ('type', EventType),
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
        ('type', EventType),
        ('player_id', PlayerID),
        ('inventory', Tuple[Inventory, ...])
    ],
    EventType.SLOT_INITIALIZED: [
        ('type', EventType),
        ('player_id', PlayerID),
        ('inventory_slot', Optional[int]),
        ('hotbar_slot', int),
        ('equipped_item', Item)
    ],
    EventType.FULL_CHUNK_LOADED: [
        ('type', EventType),
        ('position', ChunkPosition),
        ('data', bytes)
    ],
    EventType.ENTITY_LOADED: [
        ('type', EventType),
        ('player_id', PlayerID),
        ('spawn_events', Tuple[Event, ...])
    ],
    EventType.PLAYER_MOVED: [
        ('type', EventType),
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
        ('type', EventType),
        ('position', Vector3[int]),
        ('block', Block)
    ],
    EventType.ITEM_SPAWNED: [
        ('type', EventType),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('item', Item),
        ('position', Vector3[float]),
        ('motion', Vector3[float]),
        ('metadata', Tuple[EntityMetaData, ...])
    ],
    EventType.ITEM_TAKEN: [
        ('type', EventType),
        ('item_runtime_id', EntityRuntimeID),
        ('player_runtime_id', EntityRuntimeID)
    ],
    EventType.INVENTORY_UPDATED: [
        ('type', EventType),
        ('player_id', PlayerID),
        ('inventory_slot', int),
        ('slot_item', Item)
    ],
    EventType.ENTITY_REMOVED: [
        ('type', EventType),
        ('entity_runtime_id', EntityRuntimeID)
    ],
    EventType.EQUIPMENT_UPDATED: [
        ('type', EventType),
        ('entity_runtime_id', EntityRuntimeID),
        ('inventory_slot', Optional[int]),
        ('hotbar_slot', int),
        ('equipped_item', Item)
    ],
    EventType.MOB_SPAWNED: [
        ('type', EventType),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('entity_type', EntityType),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('name', Optional[str]),
        ('owner_runtime_id', Optional[EntityRuntimeID])
    ],
    EventType.MOB_MOVED: [
        ('type', EventType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('on_ground', bool)
    ]
}


event_factory = ValueObjectFactory(globals(), _event_specs, 'Event')
