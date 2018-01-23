from typing import Tuple

from pyminehub.network.address import AddressInPacket
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

__all__ = [
    'ConnectionPacket',
    'ConnectionPacketType',
    'connection_packet_factory'
]


ConnectionPacket = ValueObject


class ConnectionPacketType(ValueType):
    CONNECTED_PING = 0x00
    CONNECTED_PONG = 0x03
    CONNECTION_REQUEST = 0x09
    CONNECTION_REQUEST_ACCEPTED = 0x10
    NEW_INCOMING_CONNECTION = 0x13
    DISCONNECTION_NOTIFICATION = 0x15
    BATCH = 0xfe


_connection_packet_specs = {
    ConnectionPacketType.CONNECTED_PING: [
        ('type', ConnectionPacketType),
        ('ping_time_since_start', int)
    ],
    ConnectionPacketType.CONNECTED_PONG: [
        ('type', ConnectionPacketType),
        ('ping_time_since_start', int),
        ('pong_time_since_start', int)
    ],
    ConnectionPacketType.CONNECTION_REQUEST: [
        ('type', ConnectionPacketType),
        ('client_guid', int),
        ('client_time_since_start', int),
        ('use_encryption', bool)
    ],
    ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED: [
        ('type', ConnectionPacketType),
        ('client_address', AddressInPacket),
        ('system_index', int),
        ('internal_address', Tuple[AddressInPacket, ...]),
        ('client_time_since_start', int),
        ('server_time_since_start', int)
    ],
    ConnectionPacketType.NEW_INCOMING_CONNECTION: [
        ('type', ConnectionPacketType),
        ('server_address', AddressInPacket),
        ('internal_address', Tuple[AddressInPacket, ...]),
        ('server_time_since_start', int),
        ('client_time_since_start', int)
    ],
    ConnectionPacketType.DISCONNECTION_NOTIFICATION: [
        ('type', ConnectionPacketType)
    ],
    ConnectionPacketType.BATCH: [
        ('type', ConnectionPacketType),
        ('payloads', Tuple[bytes, ...])
    ]
}


connection_packet_factory = ValueObjectFactory(globals(), _connection_packet_specs, 'Packet')
