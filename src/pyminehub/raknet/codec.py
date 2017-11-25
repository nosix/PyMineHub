from pyminehub.binutil import *
from pyminehub.raknet.packet import ID, create


def _filter_false(value: bool) -> int:
    assert not value
    return 0


_data_structure = {
    ID.unconnected_ping: [
        ByteData(),
        LongData(),
        MagicData(),
        LongData()
    ],
    ID.unconnected_pong: [
        ByteData(),
        LongData(),
        LongData(),
        MagicData(),
        StringData()
    ],
    ID.open_connection_request1: [
        ByteData(),
        MagicData(),
        ByteData(),
        ValueFilter(RawData(), read=lambda value: len(value), write=lambda value: b'0' * value)
    ],
    ID.open_connection_reply1: [
        ByteData(),
        MagicData(),
        LongData(),
        ValueFilter(ByteData(), read=lambda value: value != 0, write=_filter_false),
        ShortData()
    ],
    ID.open_connection_request2: [
        ByteData(),
        MagicData(),
        ByteData(),
        RawData(bytes_len=4),
        ShortData(),
        ShortData(),
        LongData()
    ],
    ID.open_connection_reply2: [
        ByteData(),
        MagicData(),
        LongData(),
        ByteData(),
        RawData(bytes_len=4),
        ShortData(),
        ShortData(),
        ValueFilter(ByteData(), read=lambda value: value != 0, write=_filter_false)
    ]
}


def encode(packet: namedtuple) -> bytes:
    """ Encode packet to bytes.

    >>> p = create(ID.unconnected_pong, 58721, 472877960873915065, True, 'MCPE;')
    >>> hexlify(encode(p))
    b'1c000000000000e56106900000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b'
    """
    data = bytearray()
    encoders = _data_structure[ID(packet.id)]
    for (value, encoder) in zip(packet, encoders):
        encoder.write(data, value)
    return bytes(data)


def decode(data: bytes) -> namedtuple:
    """ Decode bytes to packet.

    >>> data = unhexlify(b'1c000000000000e56100000000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b')
    >>> decode(data)
    unconnected_pong(id=28, time_since_start=58721, server_guid=12985, valid_message_data_id=True, server_id='MCPE;')
    """
    buffer = bytearray(data)
    message_id = ID(buffer.pop(0))
    decoders = _data_structure[message_id][1:]
    args = list(decoder.read(buffer) for decoder in decoders)
    return create(message_id, *args)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
