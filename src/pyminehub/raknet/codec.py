from pyminehub.network.codec import *
from pyminehub.raknet.encapsulation import CapsuleID, capsule_factory
from pyminehub.raknet.packet import PacketID, packet_factory


_NULL_PADDING = ValueFilter(RAW_DATA, read=lambda _data: len(_data), write=lambda _value: b'0' * _value)


_packet_data_codecs = {
    PacketID.UNCONNECTED_PING: [
        LONG_DATA,
        MAGIC_DATA,
        LONG_DATA
    ],
    PacketID.UNCONNECTED_PONG: [
        LONG_DATA,
        LONG_DATA,
        MAGIC_DATA,
        STRING_DATA
    ],
    PacketID.OPEN_CONNECTION_REQUEST1: [
        MAGIC_DATA,
        BYTE_DATA,
        _NULL_PADDING
    ],
    PacketID.OPEN_CONNECTION_REPLY1: [
        MAGIC_DATA,
        LONG_DATA,
        FALSE_DATA,
        SHORT_DATA
    ],
    PacketID.OPEN_CONNECTION_REQUEST2: [
        MAGIC_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        LONG_DATA
    ],
    PacketID.OPEN_CONNECTION_REPLY2: [
        MAGIC_DATA,
        LONG_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        FALSE_DATA
    ]
}

for n in range(16):
    _packet_data_codecs[PacketID['CUSTOM_PACKET_{:X}'.format(n)]] = [
        TRIAD_DATA,
        RAW_DATA
    ]


for packet_id in (PacketID.NCK, PacketID.ACK):
    _packet_data_codecs[packet_id] = [
        SHORT_DATA,
        NamedData('range_max_equals_to_min', BOOL_DATA),
        TRIAD_DATA,
        OptionalData(TRIAD_DATA, lambda _context: _context['range_max_equals_to_min'])
    ]


class _CapsulePayload(DataCodec[bytes]):

    def read(self, data: bytearray, context: PacketCodecContext) -> bytes:
        payload_length = context['payload_length'] // 8
        d = pop_first(data, payload_length)
        context.length += payload_length
        return bytes(d)

    def write(self, data: bytearray, value: bytes, context: PacketCodecContext) -> None:
        data += value
        context.length += len(value)


_PAYLOAD_LENGTH = NamedData('payload_length', SHORT_DATA)
_CAPSULE_PAYLOAD = _CapsulePayload()


_capsule_data_codecs = {
    CapsuleID.UNRELIABLE: [
        _PAYLOAD_LENGTH,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.RELIABLE: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.RELIABLE_ORDERED: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.RELIABLE_ORDERED_HAS_SPLIT: [
        _PAYLOAD_LENGTH,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        INT_DATA,
        SHORT_DATA,
        INT_DATA,
        _CAPSULE_PAYLOAD
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_data_codecs)
capsule_codec = Codec(CapsuleID, capsule_factory, _capsule_data_codecs)
