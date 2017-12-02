import base64
import json
import zlib
from typing import Tuple

from pyminehub.binutil import *
from pyminehub.mcpe.network.packet import ConnectionRequest
from pyminehub.mcpe.network.packet import GamePacketID, game_packet_factory
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
_var_int_data = VarIntData()
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

    @classmethod
    def read(cls, data: bytearray, context: ReadContext) -> Tuple[bytes, ...]:
        payload = bytearray(zlib.decompress(data))
        payloads = []
        while len(payload) > 0:
            length = _var_int_data.read(payload, context)
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
            _var_int_data.write(data, len(v))
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


_little_endian_int_data = IntData(endian=Endian.LITTLE)


class _ConnectionRequest:

    BASE64_PADDING_BYTE = ord('=')

    @classmethod
    def _read_jwt(cls, data: bytes):
        head_base64, payload_base64, sig_base64 = data.split(b'.')
        padding = bytes(cls.BASE64_PADDING_BYTE for _ in range(len(payload_base64) % 4))
        return json.loads(base64.decodebytes(payload_base64 + padding))

    @classmethod
    def read(cls, data: bytearray, context: ReadContext) -> ConnectionRequest:
        length = _var_int_data.read(data, context)
        d = bytearray(pop_first(data, length))
        context.length += length

        local_context = ReadContext()
        chain_data = json.loads(pop_first(d, _little_endian_int_data.read(d, local_context)))
        chain_list = tuple(map(lambda chain: cls._read_jwt(bytes(chain, 'ascii')), chain_data['chain']))
        client_data_jwt = pop_first(d, _little_endian_int_data.read(d, local_context))
        client_data = cls._read_jwt(client_data_jwt)
        return ConnectionRequest(chain_list, client_data)

    @classmethod
    def write(cls, data: bytearray, value: ConnectionRequest) -> None:
        raise NotImplemented


_game_packet_converters = {
    GamePacketID.login: [
        _byte_data,
        RawData(2),
        IntData(),
        _ConnectionRequest
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
game_packet_codec = Codec(GamePacketID, game_packet_factory, _game_packet_converters)