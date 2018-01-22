"""
Codecs for connection packet
"""
import zlib
from typing import Tuple

from pyminehub.binutil.converter import pop_first, DataCodecContext, DataCodec
from pyminehub.binutil.instance import *
from pyminehub.config import get_value, ConfigKey
from pyminehub.mcpe.network.packet import *
from pyminehub.network.address import AddressInPacket
from pyminehub.network.codec import *


class _AddressList(DataCodec[Tuple[AddressInPacket, ...]]):

    def __init__(self, size: int) -> None:
        self._size = size

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[AddressInPacket, ...]:
        return tuple(ADDRESS_DATA.read(data, context) for _ in range(self._size))

    def write(self, data: bytearray, value: Tuple[AddressInPacket, ...], context: DataCodecContext) -> None:
        for i in range(self._size):
            ADDRESS_DATA.write(data, value[i], context)


class _CompressedPacketList(DataCodec[Tuple[bytes, ...]]):

    _COMPRESS_LEVEL = 7

    @staticmethod
    def _does_compress(payload: bytes) -> bool:
        return len(payload) >= get_value(ConfigKey.BATCH_COMPRESS_THRESHOLD)

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[bytes, ...]:
        payload = bytearray(zlib.decompress(data))
        context.length += len(data)
        del data[:]
        local_context = DataCodecContext()
        payloads = []
        while len(payload) > 0:
            length = VAR_INT_DATA.read(payload, local_context)
            d = pop_first(payload, length)
            payloads.append(bytes(d))
        return tuple(payloads)

    def write(self, data: bytearray, value: Tuple[bytes, ...], context: DataCodecContext) -> None:
        local_context = DataCodecContext()
        payload = bytearray()
        for v in value:
            VAR_INT_DATA.write(payload, len(v), local_context)
            payload += v
        compressed_data = zlib.compress(payload, self._COMPRESS_LEVEL if self._does_compress(payload) else 0)
        data += compressed_data
        context.length += len(compressed_data)


_packet_data_codecs = {
    ConnectionPacketType.CONNECTED_PING: [
        B_LONG_DATA
    ],
    ConnectionPacketType.CONNECTED_PONG: [
        B_LONG_DATA,
        B_LONG_DATA
    ],
    ConnectionPacketType.CONNECTION_REQUEST: [
        B_LONG_DATA,
        B_LONG_DATA,
        FALSE_DATA
    ],
    ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED: [
        ADDRESS_DATA,
        B_SHORT_DATA,
        _AddressList(20),
        B_LONG_DATA,
        B_LONG_DATA
    ],
    ConnectionPacketType.NEW_INCOMING_CONNECTION: [
        ADDRESS_DATA,
        _AddressList(20),
        B_LONG_DATA,
        B_LONG_DATA
    ],
    ConnectionPacketType.DISCONNECTION_NOTIFICATION: [
    ],
    ConnectionPacketType.BATCH: [
        _CompressedPacketList()
    ]
}


connection_packet_codec = PacketCodec(ConnectionPacketType, connection_packet_factory, _packet_data_codecs)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
