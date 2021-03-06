from typing import Optional, Tuple

from pyminehub.mcpe.const import MoveMode, EntityType
from pyminehub.mcpe.geometry import Vector3, Face, ChunkPositionWithDistance
from pyminehub.mcpe.value import PlayerID, EntityRuntimeID, Item, Hotbar
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

__all__ = [
    'Action',
    'ActionType',
    'action_factory'
]


Action = ValueObject


class ActionType(ValueType):
    LOGIN_PLAYER = 0
    REQUEST_CHUNK = 1
    MOVE_PLAYER = 2
    BREAK_BLOCK = 3
    PUT_ITEM = 4
    EQUIP = 5
    LOGOUT_PLAYER = 6
    SET_HOTBAR = 7
    REQUEST_ENTITY = 8
    SPAWN_MOB = 9
    MOVE_MOB = 10
    SET_INVENTORY = 11
    REMOVE_MOB = 12


_action_specs = {
    ActionType.LOGIN_PLAYER: [
        ('type', ActionType),
        ('player_id', PlayerID),
        ('is_guest', bool)
    ],
    ActionType.REQUEST_CHUNK: [
        ('type', ActionType),
        ('positions', Tuple[ChunkPositionWithDistance, ...]),
        ('player_runtime_id', Optional[EntityRuntimeID])
    ],
    ActionType.REQUEST_ENTITY: [
        ('type', ActionType),
        ('player_runtime_id', EntityRuntimeID)
    ],
    ActionType.MOVE_PLAYER: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('mode', MoveMode),
        ('on_ground', bool),
        ('riding_eid', EntityRuntimeID),
        ('need_response', bool)
    ],
    ActionType.BREAK_BLOCK: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[int])
    ],
    ActionType.SET_INVENTORY: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('inventory_slot', int),
        ('item', Item)
    ],
    ActionType.EQUIP: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('inventory_slot', Optional[int]),
        ('hotbar_slot', int),
        ('item', Item)
    ],
    ActionType.PUT_ITEM: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[int]),
        ('click_position', Vector3[float]),  # [0.0, 1.0]
        ('face', Face),
        ('hotbar_slot', int),
        ('item', Item)
    ],
    ActionType.LOGOUT_PLAYER: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID)
    ],
    ActionType.SET_HOTBAR: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('hotbar_slot', int),
        ('hotbar', Hotbar)
    ],
    ActionType.SPAWN_MOB: [
        ('type', ActionType),
        ('entity_type', EntityType),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('name', Optional[str]),
        ('owner_runtime_id', Optional[EntityRuntimeID])
    ],
    ActionType.MOVE_MOB: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('on_ground', bool)
    ],
    ActionType.REMOVE_MOB: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID)
    ],
}


action_factory = ValueObjectFactory(globals(), _action_specs, 'Action')
