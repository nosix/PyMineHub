from typing import Optional

from pyminehub.network.address import AddressInPacket
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

RakNetPacket = ValueObject


class RakNetPacketType(ValueType):
    UNCONNECTED_PING = 0x01
    UNCONNECTED_PONG = 0x1c
    OPEN_CONNECTION_REQUEST1 = 0x05
    OPEN_CONNECTION_REPLY1 = 0x06
    OPEN_CONNECTION_REQUEST2 = 0x07
    OPEN_CONNECTION_REPLY2 = 0x08
    FRAME_SET_0 = 0x80
    FRAME_SET_1 = 0x81
    FRAME_SET_2 = 0x82
    FRAME_SET_3 = 0x83
    FRAME_SET_4 = 0x84
    FRAME_SET_5 = 0x85
    FRAME_SET_6 = 0x86
    FRAME_SET_7 = 0x87
    FRAME_SET_8 = 0x88
    FRAME_SET_9 = 0x89
    FRAME_SET_A = 0x8a
    FRAME_SET_B = 0x8b
    FRAME_SET_C = 0x8c
    FRAME_SET_D = 0x8d
    FRAME_SET_E = 0x8e
    FRAME_SET_F = 0x8f
    NCK = 0xa0
    ACK = 0xc0


_raknet_packet_specs = {
    RakNetPacketType.UNCONNECTED_PING: [
        ('type', RakNetPacketType),
        ('time_since_start', int),
        ('valid_message_data_id', bool),
        ('client_guid', bytes)
    ],
    RakNetPacketType.UNCONNECTED_PONG: [
        ('type', RakNetPacketType),
        ('time_since_start', int),
        ('server_guid', bytes),
        ('valid_message_data_id', bool),
        ('server_id', str)
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST1: [
        ('type', RakNetPacketType),
        ('valid_message_data_id', bool),
        ('raknet_protocol_version', int),
        ('mtu_size', int)
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY1: [
        ('type', RakNetPacketType),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('use_encryption', bool),
        ('mtu_size', int)
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST2: [
        ('type', RakNetPacketType),
        ('valid_message_data_id', bool),
        ('server_address', AddressInPacket),
        ('mtu_size', int),
        ('client_guid', int)
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY2: [
        ('type', RakNetPacketType),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('client_address', AddressInPacket),
        ('mtu_size', int),
        ('use_encryption', bool)
    ]
}


for n in range(16):
    _raknet_packet_specs[RakNetPacketType['FRAME_SET_{:X}'.format(n)]] = [
        ('type', RakNetPacketType),
        ('packet_sequence_num', int),
        ('payload', bytes)
    ]


for packet_type in (RakNetPacketType.NCK, RakNetPacketType.ACK):
    _raknet_packet_specs[packet_type] = [
        ('type', RakNetPacketType),
        ('record_count', int),
        ('range_max_equals_to_min', bool),
        ('packet_sequence_number_min', int),
        ('packet_sequence_number_max', Optional[int])
    ]


raknet_packet_factory = ValueObjectFactory(globals(), _raknet_packet_specs, 'Packet')
