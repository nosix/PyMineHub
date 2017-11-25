from pyminehub.binutil import *
from pyminehub.raknet.packet import ID, create


def _filter_false(value: bool) -> int:
    assert not value
    return 0


_byte_data = ByteData()
_short_data = ShortData()
_triad_data = TriadData()
_long_data = LongData()
_magic_data = MagicData()
_string_data = StringData()
_raw_data = RawData()

_4bytes_data = RawData(bytes_len=4)
_null_padding = ValueFilter(_raw_data, read=lambda value: len(value), write=lambda value: b'0' * value)
_false_data = ValueFilter(_byte_data, read=lambda value: value != 0, write=_filter_false)


_data_structure = {
    ID.unconnected_ping: [
        _byte_data,
        _long_data,
        _magic_data,
        _long_data
    ],
    ID.unconnected_pong: [
        _byte_data,
        _long_data,
        _long_data,
        _magic_data,
        _string_data
    ],
    ID.open_connection_request1: [
        _byte_data,
        _magic_data,
        _byte_data,
        _null_padding
    ],
    ID.open_connection_reply1: [
        _byte_data,
        _magic_data,
        _long_data,
        _false_data,
        _short_data
    ],
    ID.open_connection_request2: [
        _byte_data,
        _magic_data,
        _byte_data,
        _4bytes_data,
        _short_data,
        _short_data,
        _long_data
    ],
    ID.open_connection_reply2: [
        _byte_data,
        _magic_data,
        _long_data,
        _byte_data,
        _4bytes_data,
        _short_data,
        _short_data,
        _false_data
    ]
}

for n in range(16):
    _data_structure[ID['custom_packet_{:x}'.format(n)]] = [
        _byte_data,
        _triad_data,
        _raw_data
    ]


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
