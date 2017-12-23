from typing import Tuple

from pyminehub.mcpe.geometry import ChunkPositionWithDistance
from pyminehub.mcpe.value import PlayerID
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

Action = ValueObject


class ActionType(ValueType):
    LOGIN_PLAYER = 0
    UNKNOWN1 = 1
    UNKNOWN2 = 2
    REQUEST_CHUNK = 3


_action_specs = {
    ActionType.LOGIN_PLAYER: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    ActionType.UNKNOWN1: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    ActionType.UNKNOWN2: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    ActionType.REQUEST_CHUNK: [
        ('id', int),
        ('positions', Tuple[ChunkPositionWithDistance, ...])
    ]
}


action_factory = ValueObjectFactory(_action_specs)
