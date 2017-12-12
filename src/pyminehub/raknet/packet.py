from typing import Optional

from pyminehub.network.address import AddressInPacket
from pyminehub.network.packet import PacketID, PacketFactory


class RakNetPacketID(PacketID):
    UNCONNECTED_PING = 0x01
    UNCONNECTED_PONG = 0x1c
    OPEN_CONNECTION_REQUEST1 = 0x05
    OPEN_CONNECTION_REPLY1 = 0x06
    OPEN_CONNECTION_REQUEST2 = 0x07
    OPEN_CONNECTION_REPLY2 = 0x08
    CUSTOM_PACKET_0 = 0x80
    CUSTOM_PACKET_1 = 0x81
    CUSTOM_PACKET_2 = 0x82
    CUSTOM_PACKET_3 = 0x83
    CUSTOM_PACKET_4 = 0x84
    CUSTOM_PACKET_5 = 0x85
    CUSTOM_PACKET_6 = 0x86
    CUSTOM_PACKET_7 = 0x87
    CUSTOM_PACKET_8 = 0x88
    CUSTOM_PACKET_9 = 0x89
    CUSTOM_PACKET_A = 0x8a
    CUSTOM_PACKET_B = 0x8b
    CUSTOM_PACKET_C = 0x8c
    CUSTOM_PACKET_D = 0x8d
    CUSTOM_PACKET_E = 0x8e
    CUSTOM_PACKET_F = 0x8f
    NCK = 0xa0
    ACK = 0xc0


_packet_specs = {
    RakNetPacketID.UNCONNECTED_PING: [
        ('id', int),
        ('time_since_start', int),
        ('valid_message_data_id', bool),
        ('client_guid', bytes)
    ],
    RakNetPacketID.UNCONNECTED_PONG: [
        ('id', int),
        ('time_since_start', int),
        ('server_guid', bytes),
        ('valid_message_data_id', bool),
        ('server_id', str)
    ],
    RakNetPacketID.OPEN_CONNECTION_REQUEST1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('raknet_protocol_version', int),
        ('mtu_size', int)
    ],
    RakNetPacketID.OPEN_CONNECTION_REPLY1: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('use_encryption', bool),
        ('mtu_size', int)
    ],
    RakNetPacketID.OPEN_CONNECTION_REQUEST2: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_address', AddressInPacket),
        ('mtu_size', int),
        ('client_guid', int)
    ],
    RakNetPacketID.OPEN_CONNECTION_REPLY2: [
        ('id', int),
        ('valid_message_data_id', bool),
        ('server_guid', int),
        ('client_address', AddressInPacket),
        ('mtu_size', int),
        ('use_encryption', bool)
    ]
}


for n in range(16):
    _packet_specs[RakNetPacketID['CUSTOM_PACKET_{:X}'.format(n)]] = [
        ('id', int),
        ('packet_sequence_num', int),
        ('payload', bytes)
    ]


for packet_id in (RakNetPacketID.NCK, RakNetPacketID.ACK):
    _packet_specs[packet_id] = [
        ('id', int),
        ('record_count', int),
        ('range_max_equals_to_min', bool),
        ('packet_sequence_number_min', int),
        ('packet_sequence_number_max', Optional[int])
    ]


raknet_packet_factory = PacketFactory(_packet_specs)
