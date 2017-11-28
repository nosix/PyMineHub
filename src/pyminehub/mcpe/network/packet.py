from enum import Enum
from typing import Tuple

from pyminehub.network.address import Address
from pyminehub.network.packet import PacketFactory


class PacketID(Enum):
    connection_request = 0x09
    connection_request_accepted = 0x10


_packet_specs = {
    PacketID.connection_request: [
        ('id', int),
        ('client_guid', int),
        ('time_since_start', int),
        ('use_encryption', bool)
    ],
    PacketID.connection_request_accepted: [
        ('id', int),
        ('client_address', Address),
        ('system_index', int),
        ('internal_address', Tuple[Address, ...]),
        ('time_since_start_1', int),
        ('time_since_start_2', int)
    ]
}


packet_factory = PacketFactory(_packet_specs)
