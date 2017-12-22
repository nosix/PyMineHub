from pyminehub.binutil.composite import *
from pyminehub.binutil.instance import *
from pyminehub.network.address import AddressInPacket
from pyminehub.value import ValueObject


class PacketCodec:

    def __init__(self, packet_id_cls, packet_factory, data_codecs) -> None:
        self._packet_id_cls = packet_id_cls
        self._packet_factory = packet_factory
        self._data_codecs = data_codecs

    def encode(self, packet: ValueObject, context: CompositeCodecContext=None, id_encoder: DataCodec[int]=None) -> bytes:
        """ Encode packet to bytes.

        >>> p = _packet_factory.create(PacketType.unconnected_pong, 8721, 12985, 'MCPE;')
        >>> context = CompositeCodecContext()
        >>> hexlify(_packet_codec.encode(p, context, BYTE_DATA))
        b'1c000000000000221100000000000032b900054d4350453b'
        >>> context.length
        24
        >>> context.get_values()
        (<PacketType.unconnected_pong: 28>, 8721, 12985, 'MCPE;')

        :param packet: encoding target
        :param context: if context is None then create a DataCodecContext
        :param id_encoder: a DataCodec to write packet ID
        :return: bytes data obtained by encoding
        """
        id_encoder = id_encoder or BYTE_DATA
        context = context or CompositeCodecContext()
        context.push_stack()
        data = bytearray()
        packet_id = self._packet_id_cls(packet[0])
        id_encoder.write(data, packet_id.value, context)
        context.append_value(packet_id)
        for (value, encoder) in zip(packet[1:], self._data_codecs[packet_id]):
            encoder.write(data, value, context)
            context.append_value(value)
        context.pop_stack()
        return bytes(data)

    def decode(self, data: bytes, context: CompositeCodecContext=None, id_decoder: DataCodec[int]=None) -> ValueObject:
        """ Decode bytes to packet.

        >>> data = unhexlify(b'1c000000000000221100000000000032b900054d4350453b')
        >>> context = CompositeCodecContext()
        >>> _packet_codec.decode(data, context, BYTE_DATA)
        UnconnectedPong(id=28, time_since_start=8721, server_guid=12985, server_id='MCPE;')
        >>> context.length
        24
        >>> context.get_values()
        (<PacketType.unconnected_pong: 28>, 8721, 12985, 'MCPE;')

        :param data: decoding target
        :param context: if context is None then create a DataCodecContext
        :param id_decoder: a DataCodec to read packet ID
        :return: a packet obtained by decoding
        """
        id_decoder = id_decoder or BYTE_DATA
        context = context or CompositeCodecContext()
        context.push_stack()
        buffer = bytearray(data)
        packet_id = self._packet_id_cls(id_decoder.read(buffer, context))
        context.append_value(packet_id)
        for decoder in self._data_codecs[packet_id]:
            context.append_value(decoder.read(buffer, context))
        context.pop_stack()
        return self._packet_factory.create(*context.get_values())


class AddressData(DataCodec[AddressInPacket]):
    """Convert ipv4 address.

    >>> from pyminehub.network.address import to_packet_format
    >>> c = AddressData()
    >>> data = bytearray()
    >>> context = DataCodecContext()
    >>> c.write(data, to_packet_format(('127.0.0.1', 34000)), context)
    >>> context.length
    7
    >>> hexlify(data)
    b'0480fffffe84d0'
    >>> context.clear()
    >>> c.read(data, context)
    Address(ip_version=4, address=b'\\x7f\\x00\\x00\\x01', port=34000)
    >>> context.length
    7
    >>> hexlify(data)
    b''
    """

    _IPV4_ADDRESS_DATA = RawData(4)

    def read(self, data: bytearray, context: DataCodecContext) -> AddressInPacket:
        ip_version = BYTE_DATA.read(data, context)
        ipv4_address = bytes(~b & 0xff for b in self._IPV4_ADDRESS_DATA.read(data, context))
        port = B_SHORT_DATA.read(data, context)
        return AddressInPacket(ip_version, ipv4_address, port)

    def write(self, data: bytearray, value: AddressInPacket, context: DataCodecContext) -> None:
        BYTE_DATA.write(data, value.ip_version, context)
        self._IPV4_ADDRESS_DATA.write(data, bytes(~b & 0xff for b in value.address), context)
        B_SHORT_DATA.write(data, value.port, context)


ADDRESS_DATA = AddressData()


if __name__ == '__main__':
    from binascii import hexlify, unhexlify
    from pyminehub.value import ValueType, ValueObjectFactory

    class PacketType(ValueType):
        unconnected_pong = 0x1c

    _packet_specs = {
        PacketType.unconnected_pong: [
            ('id', int),
            ('time_since_start', int),
            ('server_guid', bytes),
            ('server_id', str)
        ]
    }

    _data_codecs = {
        PacketType.unconnected_pong: [
            B_LONG_DATA,
            B_LONG_DATA,
            STRING_DATA
        ]
    }

    _packet_factory = ValueObjectFactory(_packet_specs)
    _packet_codec = PacketCodec(PacketType, _packet_factory, _data_codecs)

    import doctest
    doctest_result = doctest.testmod()
