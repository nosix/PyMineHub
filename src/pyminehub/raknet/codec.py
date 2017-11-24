from pyminehub.binutil import *
from pyminehub.raknet.packet import ID, create


_data_structure = {
    ID.UnconnectedPing: [
        ByteData(),
        LongData(),
        MagicData(),
        LongData()
    ],
    ID.UnconnectedPong: [
        ByteData(),
        LongData(),
        LongData(),
        MagicData(),
        StringData()
    ]
}


def encode(packet: namedtuple) -> bytes:
    """ Encode packet to bytes.

    >>> p = create(ID.UnconnectedPong, 58721, 472877960873915065, True, 'MCPE;')
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

    >>> data = unhexlify(b'1c000000000000e56106900000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b')
    >>> decode(data)
    UnconnectedPong(id=28, time_since_start=58721, server_guid=472877960873915065, valid_message_data_id=True, server_id='MCPE;')
    """
    buffer = bytearray(data)
    message_id = ID(buffer.pop(0))
    decoders = _data_structure[message_id][1:]
    args = list(decoder.read(buffer) for decoder in decoders)
    return create(message_id, *args)


if __name__ == '__main__':
    import doctest
    doctest.testmod()