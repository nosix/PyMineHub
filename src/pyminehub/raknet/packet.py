from enum import Enum
from typing import Union

from pyminehub.network.packet import PacketFactory


class PacketID(Enum):
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
    nck = 0xa0
    ack = 0xc0


_packet_specs = {
    PacketID.unconnected_ping: [
        ('id', int),
        ('time_since_start', int),
        ('valid_message_data_id', bool),
        ('client_guid', bytes)
    ],
    PacketID.unconnected_pong: [
        ('id', int),
        ('time_since_start', int),
        ('server_guid', bytes),
        ('valid_message_data_id', bool),
        ('server_id', str)
    ],
    PacketID.open_connection_request1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('raknet_protocol_version', int),
        ('mtu_size', int)
    ],
    PacketID.open_connection_reply1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('use_encryption', bool),
        ('mtu_size', int)
    ],
    PacketID.open_connection_request2: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_ip_version', int),
        ('server_address', bytes),
        ('server_port', int),
        ('mtu_size', int),
        ('client_guid', int)
    ],
    PacketID.open_connection_reply2: [
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
    _packet_specs[PacketID['custom_packet_{:x}'.format(n)]] = [
        ('id', int),
        ('packet_sequence_num', int),
        ('payload', bytes)
    ]


for packet_id in (PacketID.nck, PacketID.ack):
    _packet_specs[packet_id] = [
        ('id', int),
        ('record_count', int),
        ('range_max_equals_to_min', bool),
        ('packet_sequence_number_min', int),
        ('packet_sequence_number_max', Union[int, None])
    ]


packet_factory = PacketFactory(_packet_specs)
