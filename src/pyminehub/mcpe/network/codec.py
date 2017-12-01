import zlib
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
_raw_data = RawData()
_address_data = AddressData()

_false_data = ValueFilter(_byte_data, read=lambda data: data != 0, write=_filter_false)


class _AddressList:

    def __init__(self, size: int):
        self._size = size

    def read(self, data: bytearray, context: ReadContext) -> Tuple[Address, ...]:
        return tuple(_address_data.read(data, context) for _ in range(self._size))

    def write(self, data: bytearray, value: Tuple[Address, ...]) -> None:
        for i in range(self._size):
            _address_data.write(data, value[i])


class _CompressedPacketList:

    _COMPRESS_LEVEL = 7

    _length_data = VarIntData()

    @classmethod
    def read(cls, data: bytearray, context: ReadContext) -> Tuple[bytes, ...]:
        payload = bytearray(zlib.decompress(data))
        payloads = []
        while len(payload) > 0:
            length = cls._length_data.read(payload, context)
            d = pop_first(payload, length)
            if d is None:
                break
            payloads.append(d)
            context.length += length
        return tuple(payloads)

    @classmethod
    def write(cls, data: bytearray, value: Tuple[bytes, ...]) -> None:
        payload = bytearray()
        for v in value:
            cls._length_data.write(data, len(v))
            payload += v
        data += zlib.compress(payload, cls._COMPRESS_LEVEL)


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
    ],
    PacketID.batch: [
        _byte_data,
        _CompressedPacketList
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
