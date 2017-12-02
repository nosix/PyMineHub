from enum import Enum
from typing import NamedTuple, Tuple

from pyminehub.network.address import Address
from pyminehub.network.packet import PacketFactory


class PacketID(Enum):
    connected_ping = 0x00
    connected_pong = 0x03
    connection_request = 0x09
    connection_request_accepted = 0x10
    new_incoming_connection = 0x13
    batch = 0xfe


class GamePacketID(Enum):
    login = 0x01


class ConnectionRequest(NamedTuple('ConnectionRequest', [('chain', Tuple[dict, ...]), ('client', dict)])):
    pass


_packet_specs = {
    PacketID.connected_ping: [
        ('id', int),
        ('ping_time_since_start', int)
    ],
    PacketID.connected_pong: [
        ('id', int),
        ('ping_time_since_start', int),
        ('pong_time_since_start', int)
    ],
    PacketID.connection_request: [
        ('id', int),
        ('client_guid', int),
        ('client_time_since_start', int),
        ('use_encryption', bool)
    ],
    PacketID.connection_request_accepted: [
        ('id', int),
        ('client_address', Address),
        ('system_index', int),
        ('internal_address', Tuple[Address, ...]),
        ('client_time_since_start', int),
        ('server_time_since_start', int)
    ],
    PacketID.new_incoming_connection: [
        ('id', int),
        ('server_address', Address),
        ('internal_address', Tuple[Address, ...]),
        ('server_time_since_start', int),
        ('client_time_since_start', int)
    ],
    PacketID.batch: [
        ('id', int),
        ('payloads', Tuple[bytes, ...])
    ]
}


_game_packet_specs = {
    GamePacketID.login: [
        ('id', int),
        ('extra', bytes),
        ('protocol', int),
        ('connection_request', ConnectionRequest)
    ]
}


packet_factory = PacketFactory(_packet_specs)
game_packet_factory = PacketFactory(_game_packet_specs)
