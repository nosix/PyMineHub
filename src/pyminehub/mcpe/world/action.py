from pyminehub.mcpe.player import PlayerID
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory


Action = ValueObject


class ActionType(ValueType):
    LOGIN_PLAYER = 0
    UNKNOWN1 = 1


_action_specs = {
    ActionType.LOGIN_PLAYER: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    ActionType.UNKNOWN1: [
        ('id', int),
        ('player_id', PlayerID)
    ]
}


action_factory = ValueObjectFactory(_action_specs)