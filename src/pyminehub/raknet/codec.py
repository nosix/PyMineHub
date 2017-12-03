from pyminehub.network.codec import *
from pyminehub.raknet.encapsulation import CapsuleID, capsule_factory
from pyminehub.raknet.packet import PacketID, packet_factory


_NULL_PADDING = ValueFilter(RAW_DATA, read=lambda _data: len(_data), write=lambda _value: b'0' * _value)


_packet_converters = {
    PacketID.unconnected_ping: [
        LONG_DATA,
        MAGIC_DATA,
        LONG_DATA
    ],
    PacketID.unconnected_pong: [
        LONG_DATA,
        LONG_DATA,
        MAGIC_DATA,
        STRING_DATA
    ],
    PacketID.open_connection_request1: [
        MAGIC_DATA,
        BYTE_DATA,
        _NULL_PADDING
    ],
    PacketID.open_connection_reply1: [
        MAGIC_DATA,
        LONG_DATA,
        FALSE_DATA,
        SHORT_DATA
    ],
    PacketID.open_connection_request2: [
        MAGIC_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        LONG_DATA
    ],
    PacketID.open_connection_reply2: [
        MAGIC_DATA,
        LONG_DATA,
        ADDRESS_DATA,
        SHORT_DATA,
        FALSE_DATA
    ]
}

for n in range(16):
    _packet_converters[PacketID['custom_packet_{:x}'.format(n)]] = [
        TRIAD_DATA,
        RAW_DATA
    ]


for packet_id in (PacketID.nck, PacketID.ack):
    _packet_converters[packet_id] = [
        SHORT_DATA,
        BOOL_DATA,
        TRIAD_DATA,
        PassIf(TRIAD_DATA, lambda _context: _context.values[2])
    ]


class _CapsulePayload(DataCodec[bytes]):

    def read(self, data: bytearray, context: PacketCodecContext) -> bytes:
        payload_length = context.values[1] // 8
        d = pop_first(data, payload_length)
        context.length += payload_length
        return bytes(d)

    def write(self, data: bytearray, value: bytes, context: PacketCodecContext) -> None:
        data += value
        context.length += len(value)


_CAPSULE_PAYLOAD = _CapsulePayload()


_capsule_converters = {
    CapsuleID.unreliable: [
        SHORT_DATA,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.reliable: [
        SHORT_DATA,
        TRIAD_DATA,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.reliable_ordered: [
        SHORT_DATA,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        _CAPSULE_PAYLOAD
    ],
    CapsuleID.reliable_ordered_has_split: [
        SHORT_DATA,
        TRIAD_DATA,
        TRIAD_DATA,
        BYTE_DATA,
        INT_DATA,
        SHORT_DATA,
        INT_DATA,
        _CAPSULE_PAYLOAD
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
capsule_codec = Codec(CapsuleID, capsule_factory, _capsule_converters)
