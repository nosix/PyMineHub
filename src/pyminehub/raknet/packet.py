from enum import Enum
from typing import NamedTuple


class ID(Enum):
    unconnected_ping = 0x01
    unconnected_pong = 0x1c
    open_connection_request1 = 0x05
    open_connection_reply1 = 0x06
    open_connection_request2 = 0x07
    open_connection_reply2 = 0x08


_packet_specs = {
    ID.unconnected_ping: [
        ('id', int),
        ('time_since_start', int),
        ('valid_message_data_id', bool),
        ('client_guid', bytes)
    ],
    ID.unconnected_pong: [
        ('id', int),
        ('time_since_start', int),
        ('server_guid', bytes),
        ('valid_message_data_id', bool),
        ('server_id', str)
    ],
    ID.open_connection_request1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('raknet_protocol_version', int),
        ('mtu_size', int)
    ],
    ID.open_connection_reply1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('use_encryption', bool),
        ('mtu_size', int)
    ],
    ID.open_connection_request2: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_ip_version', int),
        ('server_address', bytes),
        ('server_port', int),
        ('mtu_size', int),
        ('client_guid', int)
    ],
    ID.open_connection_reply2: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('client_ip_version', int),
        ('client_address', bytes),
        ('client_port', int),
        ('mtu_size', int),
        ('use_encryption', bool)
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
        ID.unconnected_ping,
        4580544,
        True,
        to_bytes('04:40:00:00:09:17:af:e5')))
    print(create(
        ID.unconnected_pong,
        58721,
        to_bytes('06:90:00:00:00:00:32:b9'),
        True,
        'MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'))
