from typing import NamedTuple, Optional

from pyminehub.binutil import *
from pyminehub.network.address import Address

BYTE_DATA = ByteData()
SHORT_DATA = ShortData()
TRIAD_DATA = TriadData()
INT_DATA = IntData()
LONG_DATA = LongData()
BYTES_DATA = BytesData()
STRING_DATA = StringData()
RAW_DATA = RawData()


class PacketCodecContext(DataCodecContext):

    def __init__(self):
        super().__init__()
        self.values = []


class Codec:

    def __init__(self, packet_id_cls, packet_factory, data_codecs):
        self._packet_id_cls = packet_id_cls
        self._packet_factory = packet_factory
        self._data_codecs = data_codecs

    def encode(self, packet: NamedTuple, context: PacketCodecContext=None, id_encoder: DataCodec[int]=None) -> bytes:
        """ Encode packet to bytes.

        >>> p = packet_factory.create(ID.unconnected_pong, 8721, 12985, True, 'MCPE;')
        >>> context = PacketCodecContext()
        >>> hexlify(packet_codec.encode(p, context, BYTE_DATA))
        b'1c000000000000221100000000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b'
        >>> context.length
        40
        >>> context.values
        [<ID.unconnected_pong: 28>, 8721, 12985, True, 'MCPE;']

        :param packet: encoding target
        :param context: if context is None then create a DataCodecContext
        :param id_encoder: a DataCodec to write packet ID
        :return: bytes data obtained by encoding
        """
        id_encoder = id_encoder or BYTE_DATA
        context = context or PacketCodecContext()
        data = bytearray()
        packet_id = self._packet_id_cls(packet[0])
        id_encoder.write(data, packet_id.value, context)
        context.values.append(packet_id)
        for (value, encoder) in zip(packet[1:], self._data_codecs[packet_id]):
            encoder.write(data, value, context)
            context.values.append(value)
        return bytes(data)

    def decode(self, data: bytes, context: PacketCodecContext=None, id_decoder: DataCodec[int]=None) -> NamedTuple:
        """ Decode bytes to packet.

        >>> data = unhexlify(b'1c000000000000221100000000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b')
        >>> context = PacketCodecContext()
        >>> packet_codec.decode(data, context, BYTE_DATA)
        unconnected_pong(id=28, time_since_start=8721, server_guid=12985, valid_message_data_id=True, server_id='MCPE;')
        >>> context.length
        40
        >>> context.values
        [<ID.unconnected_pong: 28>, 8721, 12985, True, 'MCPE;']

        :param data: decoding target
        :param context: if context is None then create a DataCodecContext
        :param id_decoder: a DataCodec to read packet ID
        :return: a packet obtained by decoding
        """
        id_decoder = id_decoder or BYTE_DATA
        context = context or PacketCodecContext()
        buffer = bytearray(data)
        packet_id = self._packet_id_cls(id_decoder.read(buffer, context))
        context.values.append(packet_id)
        for decoder in self._data_codecs[packet_id]:
            context.values.append(decoder.read(buffer, context))
        return self._packet_factory.create(*context.values)


class MagicData(DataCodec[bool]):
    """Check MAGIC data that is '00:ff:ff:00:fe:fe:fe:fe:fd:fd:fd:fd:12:34:56:78'.

    >>> c = MagicData()
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
        return d == MagicData.BYTES

    def write(self, data: bytearray, is_valid: bool, context: DataCodecContext) -> None:
        assert is_valid
        data += MagicData.BYTES
        context.length += self._LENGTH


class AddressData(DataCodec[Address]):
    """Convert ipv4 address.

    >>> from pyminehub.network.address import to_address
    >>> c = AddressData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, to_address(('127.0.0.1', 34000)), context)
    >>> context.length
    7
    >>> hexlify(data)
    b'047f00000184d0'
    >>> context.clear()
    >>> c.read(data, context)
    Address(ip_version=4, address=b'\\x7f\\x00\\x00\\x01', port=34000)
    >>> context.length
    7
    >>> hexlify(data)
    b''
    """

    _IPV4_ADDRESS_DATA = RawData(4)

    def read(self, data: bytearray, context: DataCodecContext) -> Address:
        ip_version = BYTE_DATA.read(data, context)
        ipv4_address = self._IPV4_ADDRESS_DATA.read(data, context)
        port = SHORT_DATA.read(data, context)
        return Address(ip_version, ipv4_address, port)

    def write(self, data: bytearray, value: Address, context: DataCodecContext) -> None:
        BYTE_DATA.write(data, value.ip_version, context)
        self._IPV4_ADDRESS_DATA.write(data, value.address, context)
        SHORT_DATA.write(data, value.port, context)


class PassIf(DataCodec[T]):
    """Pass if predicate is true.

    >>> c = PassIf(BYTE_DATA, lambda _context: _context.values[0])
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> context.values = [False]
    >>> c.write(data, 255, context)
    >>> context.length
    1
    >>> hexlify(data)
    b'ff'
    >>> context.clear()
    >>> c.read(data, context)
    255
    >>> context.length
    1
    >>> hexlify(data)
    b''
    >>> context.clear()
    >>> context.values = [True]
    >>> c.write(data, 255, context)
    >>> context.length
    0
    >>> hexlify(data)
    b''
    >>> context.clear()
    >>> c.read(data, context)
    >>> context.length
    0
    >>> hexlify(data)
    b''
    """

    def __init__(self, data_codec: DataCodec[T], predicate: Callable[[DataCodecContext], bool]):
        self._data_codec = data_codec
        self._predicate = predicate

    def read(self, data: bytearray, context: DataCodecContext) -> Optional[T]:
        return self._data_codec.read(data, context) if not self._predicate(context) else None

    def write(self, data: bytearray, value: Optional[T], context: DataCodecContext) -> None:
        if not self._predicate(context):
            if value is None:
                raise BytesOperationError('Decoding needs the Value.')
            # noinspection PyTypeChecker
            self._data_codec.write(data, value, context)


def _only_false(value: bool) -> int:
    assert not value
    return 0


MAGIC_DATA = MagicData()
ADDRESS_DATA = AddressData()
BOOL_DATA = ValueFilter(BYTE_DATA, read=lambda _data: _data != 0, write=lambda _value: 1 if _value else 0)
FALSE_DATA = ValueFilter(BYTE_DATA, read=lambda _data: _data != 0, write=_only_false)


if __name__ == '__main__':
    from enum import Enum
    from binascii import hexlify, unhexlify
    from pyminehub.network.packet import PacketFactory

    class ID(Enum):
        unconnected_pong = 0x1c

    _packet_specs = {
        ID.unconnected_pong: [
            ('id', int),
            ('time_since_start', int),
            ('server_guid', bytes),
            ('valid_message_data_id', bool),
            ('server_id', str)
        ]
    }

    _data_codecs = {
        ID.unconnected_pong: [
            LONG_DATA,
            LONG_DATA,
            MAGIC_DATA,
            STRING_DATA
        ]
    }

    packet_factory = PacketFactory(_packet_specs)
    packet_codec = Codec(ID, packet_factory, _data_codecs)

    import doctest
    doctest.testmod()
