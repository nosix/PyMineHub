from pyminehub.network.codec import *
from pyminehub.raknet.frame import RakNetFrameType, raknet_frame_factory
from pyminehub.raknet.packet import RakNetPacketType, raknet_packet_factory


class _MtuSizeData(DataCodec[int]):

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        RAW_DATA.read(data, context)
        return context.length

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        RAW_DATA.write(data, b'0' * (value - context.length), context)


_packet_data_codecs = {
    RakNetPacketType.UNCONNECTED_PING: [
        LONG_DATA,
        MAGIC_DATA,
        LONG_DATA
    ],
    RakNetPacketType.UNCONNECTED_PONG: [
        LONG_DATA,
        LONG_DATA,
        MAGIC_DATA,
        STRING_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST1: [
        MAGIC_DATA,
        BYTE_DATA,
        _MtuSizeData()
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY1: [
        MAGIC_DATA,
        LONG_DATA,
        FALSE_DATA,
        SHORT_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST2: [
        MAGIC_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        LONG_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY2: [
        MAGIC_DATA,
        LONG_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        FALSE_DATA
    ]
}

for n in range(16):
    _packet_data_codecs[RakNetPacketType['FRAME_SET_{:X}'.format(n)]] = [
        TRIAD_DATA,
        RAW_DATA
    ]


for packet_id in (RakNetPacketType.NCK, RakNetPacketType.ACK):
    _packet_data_codecs[packet_id] = [
        SHORT_DATA,
        NamedData('range_max_equals_to_min', BOOL_DATA),
        TRIAD_DATA,
        OptionalData(TRIAD_DATA, lambda _context: _context['range_max_equals_to_min'])
    ]


class _FramePayload(DataCodec[bytes]):

    def read(self, data: bytearray, context: PacketCodecContext) -> bytes:
        payload_length = context['payload_length'] // 8
        d = pop_first(data, payload_length)
        context.length += payload_length
        return bytes(d)

    def write(self, data: bytearray, value: bytes, context: PacketCodecContext) -> None:
        data += value
        context.length += len(value)


_PAYLOAD_LENGTH = NamedData('payload_length', SHORT_DATA)
_FRAME_PAYLOAD = _FramePayload()


_frame_data_codecs = {
    RakNetFrameType.UNRELIABLE: [
        _PAYLOAD_LENGTH,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE_ORDERED: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        INT_DATA,
        SHORT_DATA,
        INT_DATA,
        _FRAME_PAYLOAD
    ]
}


raknet_packet_codec = Codec(RakNetPacketType, raknet_packet_factory, _packet_data_codecs)
raknet_frame_codec = Codec(RakNetFrameType, raknet_frame_factory, _frame_data_codecs)
