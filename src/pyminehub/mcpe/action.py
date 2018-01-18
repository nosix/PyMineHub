from pyminehub.mcpe.value import *
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

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


_action_specs = {
    ActionType.LOGIN_PLAYER: [
        ('type', ActionType),
        ('player_id', PlayerID)
    ],
    ActionType.REQUEST_CHUNK: [
        ('type', ActionType),
        ('positions', Tuple[ChunkPositionWithDistance, ...])
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
        ('riding_eid', EntityRuntimeID)
    ],
    ActionType.BREAK_BLOCK: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[int])
    ],
    ActionType.PUT_ITEM: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[int]),
        ('face', Face),
        ('hotbar_slot', int),
        ('item', Item)
    ],
    ActionType.EQUIP: [
        ('type', ActionType),
        ('entity_runtime_id', EntityRuntimeID),
        ('inventory_slot', Optional[int]),
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
    ]
}


action_factory = ValueObjectFactory(globals(), _action_specs, 'Action')
