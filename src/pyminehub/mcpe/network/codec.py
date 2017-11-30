from typing import Tuple

from pyminehub.binutil import *
from pyminehub.mcpe.network.packet import PacketID, packet_factory
from pyminehub.network.address import Address
from pyminehub.network.codec import Codec, AddressData


def _filter_false(value: bool) -> int:
    assert not value
    return 0


_byte_data = ByteData()
_short_data = ShortData()
_long_data = LongData()
_address_data = AddressData()

_false_data = ValueFilter(_byte_data, read=lambda value: value != 0, write=_filter_false)


class _AddressList:

    def __init__(self, size: int):
        self._size = size

    def read(self, data: bytearray, context: ReadContext) -> Tuple[Address, ...]:
        return tuple(_address_data.read(data, context) for _ in range(self._size))

    def write(self, data: bytearray, value: Tuple[Address, ...]) -> None:
        for i in range(self._size):
            _address_data.write(data, value[i])


_packet_converters = {
    PacketID.connected_ping: [
        _byte_data,
        _long_data
    ],
    PacketID.connected_pong: [
        _byte_data,
        _long_data,
        _long_data
    ],
    PacketID.connection_request: [
        _byte_data,
        _long_data,
        _long_data,
        _false_data
    ],
    PacketID.connection_request_accepted: [
        _byte_data,
        _address_data,
        _short_data,
        _AddressList(20),
        _long_data,
        _long_data
    ],
    PacketID.new_incoming_connection: [
        _byte_data,
        _address_data,
        _AddressList(20),
        _long_data,
        _long_data
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
