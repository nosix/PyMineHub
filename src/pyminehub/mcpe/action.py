from pyminehub.mcpe.value import *
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

Action = ValueObject


class ActionType(ValueType):
    LOGIN_PLAYER = 0
    REQUEST_CHUNK = 1
    MOVE_PLAYER = 2


_action_specs = {
    ActionType.LOGIN_PLAYER: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    ActionType.REQUEST_CHUNK: [
        ('id', int),
        ('positions', Tuple[ChunkPositionWithDistance, ...])
    ],
    ActionType.MOVE_PLAYER: [
        ('id', int),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('mode', MoveMode),
        ('on_ground', bool),
        ('riding_eid', EntityRuntimeID)
    ]
}


action_factory = ValueObjectFactory(_action_specs)