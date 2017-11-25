from enum import Enum

from pyminehub.network.packet import PacketFactory


class PacketID(Enum):
    connection_request = 0x09


_packet_specs = {
    PacketID.connection_request: [
        ('id', int),
        ('client_guid', int),
        ('time_since_start', int),
        ('use_encryption', bool)
    ]
}


packet_factory = PacketFactory(_packet_specs)