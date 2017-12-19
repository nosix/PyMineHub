from pyminehub.mcpe.player import PlayerID
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory


Event = ValueObject


class EventType(ValueType):
    PLAYER_LOGGED_IN = 0
    UNKNOWN1 = 1


_event_specs = {
    EventType.PLAYER_LOGGED_IN: [
        ('id', int),
        ('player_id', PlayerID)
    ],
    EventType.UNKNOWN1: [
        ('id', int),
        ('player_id', PlayerID)
    ]
}


event_factory = ValueObjectFactory(_event_specs)
