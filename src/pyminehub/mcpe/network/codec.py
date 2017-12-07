import base64
import json
import zlib

from pyminehub.config import get_value, ConfigKey
from pyminehub.mcpe.network.packet import *
from pyminehub.network.codec import *

_LITTLE_ENDIAN_SHORT_DATA = ShortData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_INT_DATA = IntData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_LONG_DATA = LongData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_FLOAT_DATA = FloatData(endian=Endian.LITTLE)

_VAR_INT_LENGTH_STRING_DATA = StringData(len_codec=VarIntData())

_HEADER_EXTRA_DATA = RawData(2)


class _AddressList(DataCodec[Tuple[Address, ...]]):

    def __init__(self, size: int):
        self._size = size

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[Address, ...]:
        return tuple(ADDRESS_DATA.read(data, context) for _ in range(self._size))

    def write(self, data: bytearray, value: Tuple[Address, ...], context: DataCodecContext) -> None:
        for i in range(self._size):
            ADDRESS_DATA.write(data, value[i], context)


class _CompressedPacketList(DataCodec[Tuple[bytes, ...]]):

    _COMPRESS_LEVEL = 7

    @staticmethod
    def _does_compress(payload: bytes) -> bool:
        return len(payload) >= get_value(ConfigKey.batch_compress_threshold)

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[bytes, ...]:
        payload = bytearray(zlib.decompress(data))
        context.length += len(data)
        del data[:]
        local_context = DataCodecContext()
        payloads = []
        while len(payload) > 0:
            length = VAR_INT_DATA.read(payload, local_context)
            d = pop_first(payload, length)
            payloads.append(d)
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
    PacketID.connected_ping: [
        LONG_DATA
    ],
    PacketID.connected_pong: [
        LONG_DATA,
        LONG_DATA
    ],
    PacketID.connection_request: [
        LONG_DATA,
        LONG_DATA,
        FALSE_DATA
    ],
    PacketID.connection_request_accepted: [
        ADDRESS_DATA,
        SHORT_DATA,
        _AddressList(20),
        LONG_DATA,
        LONG_DATA
    ],
    PacketID.new_incoming_connection: [
        ADDRESS_DATA,
        _AddressList(20),
        LONG_DATA,
        LONG_DATA
    ],
    PacketID.batch: [
        _CompressedPacketList()
    ]
}


class _ConnectionRequest(DataCodec[ConnectionRequest]):

    BASE64_PADDING_BYTE = ord('=')

    @classmethod
    def _read_jwt(cls, data: bytes):
        head_base64, payload_base64, sig_base64 = data.split(b'.')
        padding = bytes(cls.BASE64_PADDING_BYTE for _ in range(len(payload_base64) % 4))
        return json.loads(base64.decodebytes(payload_base64 + padding))

    def read(self, data: bytearray, context: DataCodecContext) -> ConnectionRequest:
        length = VAR_INT_DATA.read(data, context)
        d = bytearray(pop_first(data, length))
        context.length += length

        local_context = DataCodecContext()
        chain_data = json.loads(pop_first(d, _LITTLE_ENDIAN_INT_DATA.read(d, local_context)))
        chain_list = tuple(map(lambda chain: self._read_jwt(bytes(chain, 'ascii')), chain_data['chain']))
        client_data_jwt = pop_first(d, _LITTLE_ENDIAN_INT_DATA.read(d, local_context))
        client_data = self._read_jwt(client_data_jwt)
        return ConnectionRequest(chain_list, client_data)

    def write(self, data: bytearray, value: ConnectionRequest, context: DataCodecContext) -> None:
        raise NotImplemented


class _VarListData(DataCodec[Tuple[T, ...]]):

    def __init__(self, item_codec: DataCodec[T], count_codec: DataCodec[int]=_LITTLE_ENDIAN_SHORT_DATA):
        self._item_codec = item_codec
        self._count_codec = count_codec

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[PackEntry, ...]:
        count = self._count_codec.read(data, context)
        return tuple(self._item_codec.read(data, context) for _ in range(count))

    def write(self, data: bytearray, value: Tuple[T, ...], context: DataCodecContext) -> None:
        self._count_codec.write(data, len(value), context)
        for entry in value:
            self._item_codec.write(data, entry, context)


class _PackEntry(DataCodec[PackEntry]):

    def read(self, data: bytearray, context: DataCodecContext) -> PackEntry:
        pack_id = STRING_DATA.read(data, context)
        pack_version = STRING_DATA.read(data, context)
        pack_size = _LITTLE_ENDIAN_LONG_DATA.read(data, context)
        STRING_DATA.read(data, context)  # TODO
        STRING_DATA.read(data, context)  # TODO
        return PackEntry(pack_id, pack_version, pack_size)

    def write(self, data: bytearray, value: PackEntry, context: DataCodecContext) -> None:
        STRING_DATA.write(data, value.id, context)
        STRING_DATA.write(data, value.version, context)
        _LITTLE_ENDIAN_LONG_DATA.write(data, value.size, context)
        STRING_DATA.write(data, '', context)
        STRING_DATA.write(data, '', context)


class _PackStack(DataCodec[PackStack]):

    def read(self, data: bytearray, context: DataCodecContext) -> PackStack:
        pack_id = STRING_DATA.read(data, context)
        pack_version = STRING_DATA.read(data, context)
        STRING_DATA.read(data, context)  # TODO
        return PackStack(pack_id, pack_version)

    def write(self, data: bytearray, value: PackStack, context: DataCodecContext) -> None:
        STRING_DATA.write(data, value.id, context)
        STRING_DATA.write(data, value.version, context)
        STRING_DATA.write(data, '', context)


class _Vector3Data(DataCodec[Vector3]):

    def read(self, data: bytearray, context: DataCodecContext) -> Vector3:
        x = _LITTLE_ENDIAN_FLOAT_DATA.read(data, context)
        z = _LITTLE_ENDIAN_FLOAT_DATA.read(data, context)
        y = _LITTLE_ENDIAN_FLOAT_DATA.read(data, context)
        return Vector3(x, z, y)

    def write(self, data: bytearray, value: T, context: DataCodecContext) -> None:
        _LITTLE_ENDIAN_FLOAT_DATA.write(data, value.x, context)
        _LITTLE_ENDIAN_FLOAT_DATA.write(data, value.z, context)
        _LITTLE_ENDIAN_FLOAT_DATA.write(data, value.y, context)


class _GameRule(DataCodec[GameRule]):

    _TYPE_MAP = {
        1: BOOL_DATA,
        2: VAR_INT_DATA,
        3: _LITTLE_ENDIAN_FLOAT_DATA
    }

    def read(self, data: bytearray, context: DataCodecContext) -> GameRule:
        rule_name = _VAR_INT_LENGTH_STRING_DATA.read(data, context)
        rule_type = VAR_INT_DATA.read(data, context)
        rule_value = self._TYPE_MAP[rule_type].read(data, context)
        return GameRule(rule_name, rule_type, rule_value)

    def write(self, data: bytearray, value: T, context: DataCodecContext) -> None:
        _VAR_INT_LENGTH_STRING_DATA.write(data, value.name, context)
        VAR_INT_DATA.write(data, value.type, context)
        self._TYPE_MAP[value.type].write(data, value.value, context)


_VECTOR3_DATA = _Vector3Data()


_game_data_codecs = {
    GamePacketID.login: [
        _HEADER_EXTRA_DATA,
        INT_DATA,
        _ConnectionRequest()
    ],
    GamePacketID.play_status: [
        _HEADER_EXTRA_DATA,
        ValueFilter(INT_DATA, read=lambda _data: PlayStatus(_data), write=lambda _value: _value.value)
    ],
    GamePacketID.resource_packs_info: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _VarListData(_PackEntry()),
        _VarListData(_PackEntry())
    ],
    GamePacketID.resource_pack_stack: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _VarListData(_PackStack(), VAR_INT_DATA),
        _VarListData(_PackStack(), VAR_INT_DATA)
    ],
    GamePacketID.resource_pack_client_response: [
        _HEADER_EXTRA_DATA,
        ValueFilter(BYTE_DATA, read=lambda _data: ResourcePackStatus(_data), write=lambda _value: _value.value),
        _VarListData(STRING_DATA)
    ],
    GamePacketID.start_game: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _VECTOR3_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        ValueFilter(VAR_INT_DATA, read=lambda _data: Generator(_data), write=lambda _value: _value.value),
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        BOOL_DATA,
        VAR_INT_DATA,
        BOOL_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,  # TODO confirm correctness
        _LITTLE_ENDIAN_FLOAT_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        _VarListData(_GameRule(), VAR_INT_DATA),
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        BOOL_DATA,
        BOOL_DATA,
        _LITTLE_ENDIAN_LONG_DATA,
        VAR_INT_DATA
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_data_codecs)
game_packet_codec = Codec(GamePacketID, game_packet_factory, _game_data_codecs)


if __name__ == '__main__':
    def print_packet_info(specs, data_codecs):
        for packet_id, spec in specs.items():
            data_codec = data_codecs[packet_id]
            print(packet_id, ':')
            assert len(spec[1:]) == len(data_codec), '{} != {}'.format(len(spec[1:]), len(data_codec))
            for data_spec, data_codec in zip(spec[1:], data_codec):
                orig_base = str(type(data_codec).__dict__['__orig_bases__'][0])
                print('  ', data_spec[0], ':', data_spec[1].__name__, '=',
                      type(data_codec).__name__ + orig_base.split('DataCodec')[-1])
    # noinspection PyProtectedMember
    from pyminehub.mcpe.network.packet import _game_packet_specs
    print_packet_info(_game_packet_specs, _game_data_codecs)
