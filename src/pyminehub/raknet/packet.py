from enum import Enum
from typing import NamedTuple


class ID(Enum):
    UnconnectedPing = 0x01
    UnconnectedPong = 0x1c


_packet_specs = {
    ID.UnconnectedPing: [
        ('id', int),
        ('time_since_start', int),
        ('valid_message_data_id', bool),
        ('client_guid', bytes)
    ],
    ID.UnconnectedPong: [
        ('id', int),
        ('time_since_start', int),
        ('server_guid', bytes),
        ('valid_message_data_id', bool),
        ('server_id', str)
    ]
}


_factory = dict(
    (message_id, NamedTuple(message_id.name, field_names)) for message_id, field_names in _packet_specs.items())


def create(message_id: ID, *args):
    # noinspection PyCallingNonCallable
    return _factory[message_id](message_id.value, *args)


if __name__ == '__main__':
    from pyminehub.binutil import to_bytes
    print(create(
        ID.UnconnectedPing,
        4580544,
        True,
        to_bytes('04:40:00:00:09:17:af:e5')))
    print(create(
        ID.UnconnectedPong,
        58721,
        to_bytes('06:90:00:00:00:00:32:b9'),
        True,
        'MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'))