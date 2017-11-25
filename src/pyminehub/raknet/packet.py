from enum import Enum
from typing import NamedTuple


class ID(Enum):
    unconnected_ping = 0x01
    unconnected_pong = 0x1c
    open_connection_request1 = 0x05
    open_connection_reply1 = 0x06
    open_connection_request2 = 0x07
    open_connection_reply2 = 0x08
    custom_packet_0 = 0x80
    custom_packet_1 = 0x81
    custom_packet_2 = 0x82
    custom_packet_3 = 0x83
    custom_packet_4 = 0x84
    custom_packet_5 = 0x85
    custom_packet_6 = 0x86
    custom_packet_7 = 0x87
    custom_packet_8 = 0x88
    custom_packet_9 = 0x89
    custom_packet_a = 0x8a
    custom_packet_b = 0x8b
    custom_packet_c = 0x8c
    custom_packet_d = 0x8d
    custom_packet_e = 0x8e
    custom_packet_f = 0x8f


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

for n in range(16):
    _packet_specs[ID['custom_packet_{:x}'.format(n)]] = [
        ('id', int),
        ('packet_sequence_num', int),
        ('payload', bytes)
    ]


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
