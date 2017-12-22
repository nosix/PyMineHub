from pyminehub.network.codec import *
from pyminehub.raknet.frame import RakNetFrameType, raknet_frame_factory
from pyminehub.raknet.packet import RakNetPacketType, raknet_packet_factory


class _MtuSizeData(DataCodec[int]):

    def read(self, data: bytearray, context: DataCodecContext) -> int:
        RAW_DATA.read(data, context)
        return context.length

    def write(self, data: bytearray, value: int, context: DataCodecContext) -> None:
        RAW_DATA.write(data, b'0' * (value - context.length), context)


class _MagicData(DataCodec[bool]):
    """Check MAGIC data that is '00:ff:ff:00:fe:fe:fe:fe:fd:fd:fd:fd:12:34:56:78'.

    >>> c = _MagicData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, True, context)
    >>> context.length
    16
    >>> hexlify(data)
    b'00ffff00fefefefefdfdfdfd12345678'
    >>> context.clear()
    >>> c.read(data, context)
    True
    >>> context.length
    16
    >>> hexlify(data)
    b''
    >>> c.read(bytearray(b'ffffff00fefefefefdfdfdfd12345678'), context)
    False
    """

    BYTES = unhexlify(b'00ffff00fefefefefdfdfdfd12345678')

    _LENGTH = len(BYTES)

    def read(self, data: bytearray, context: DataCodecContext) -> bool:
        d = pop_first(data, self._LENGTH)
        context.length += self._LENGTH
        return d == _MagicData.BYTES

    def write(self, data: bytearray, is_valid: bool, context: DataCodecContext) -> None:
        assert is_valid
        data += _MagicData.BYTES
        context.length += self._LENGTH


_MAGIC_DATA = _MagicData()


_packet_data_codecs = {
    RakNetPacketType.UNCONNECTED_PING: [
        B_LONG_DATA,
        _MAGIC_DATA,
        B_LONG_DATA
    ],
    RakNetPacketType.UNCONNECTED_PONG: [
        B_LONG_DATA,
        B_LONG_DATA,
        _MAGIC_DATA,
        STRING_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST1: [
        _MAGIC_DATA,
        BYTE_DATA,
        _MtuSizeData()
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY1: [
        _MAGIC_DATA,
        B_LONG_DATA,
        FALSE_DATA,
        B_SHORT_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REQUEST2: [
        _MAGIC_DATA,
        ADDRESS_DATA,
        B_SHORT_DATA,
        B_LONG_DATA
    ],
    RakNetPacketType.OPEN_CONNECTION_REPLY2: [
        _MAGIC_DATA,
        B_LONG_DATA,
        ADDRESS_DATA,
        B_SHORT_DATA,
        FALSE_DATA
    ]
}

for n in range(16):
    _packet_data_codecs[RakNetPacketType['FRAME_SET_{:X}'.format(n)]] = [
        L_TRIAD_DATA,
        RAW_DATA
    ]


for packet_id in (RakNetPacketType.NCK, RakNetPacketType.ACK):
    _packet_data_codecs[packet_id] = [
        B_SHORT_DATA,
        NamedData('range_max_equals_to_min', BOOL_DATA),
        L_TRIAD_DATA,
        OptionalData(L_TRIAD_DATA, lambda _context: _context['range_max_equals_to_min'])
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


_PAYLOAD_LENGTH = NamedData('payload_length', B_SHORT_DATA)
_FRAME_PAYLOAD = _FramePayload()


_frame_data_codecs = {
    RakNetFrameType.UNRELIABLE: [
        _PAYLOAD_LENGTH,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE: [
        _PAYLOAD_LENGTH,
        L_TRIAD_DATA,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE_ORDERED: [
        _PAYLOAD_LENGTH,
        L_TRIAD_DATA,
        L_TRIAD_DATA,
        BYTE_DATA,
        _FRAME_PAYLOAD
    ],
    RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: [
        _PAYLOAD_LENGTH,
        L_TRIAD_DATA,
        L_TRIAD_DATA,
        BYTE_DATA,
        B_INT_DATA,
        B_SHORT_DATA,
        B_INT_DATA,
        _FRAME_PAYLOAD
    ]
}


raknet_packet_codec = Codec(RakNetPacketType, raknet_packet_factory, _packet_data_codecs)
raknet_frame_codec = Codec(RakNetFrameType, raknet_frame_factory, _frame_data_codecs)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
