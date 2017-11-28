from typing import NamedTuple

from pyminehub.network.address import Address


class Codec:

    def __init__(self, packet_id_cls, packet_factory, data_converters):
        self._packet_id_cls = packet_id_cls
        self._packet_factory = packet_factory
        self._data_converters = data_converters

    def encode(self, packet: NamedTuple) -> bytes:
        """ Encode packet to bytes.

        >>> p = factory.create(ID.unconnected_pong, 58721, 472877960873915065, True, 'MCPE;')
        >>> hexlify(codec.encode(p))
        b'1c000000000000e56106900000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b'
        """
        data = bytearray()
        # noinspection PyUnresolvedReferences
        encoders = self._data_converters[self._packet_id_cls(packet.id)]
        for (value, encoder) in zip(packet, encoders):
            encoder.write(data, value)
        return bytes(data)

    def decode(self, data: bytes) -> NamedTuple:
        """ Decode bytes to packet.

        >>> data = unhexlify(b'1c000000000000221100000000000032b900ffff00fefefefefdfdfdfd1234567800054d4350453b')
        >>> codec.decode(data)
        unconnected_pong(id=28, time_since_start=8721, server_guid=12985, valid_message_data_id=True, server_id='MCPE;')
        """
        buffer = bytearray(data)
        packet_id = self._packet_id_cls(buffer.pop(0))
        decoders = self._data_converters[packet_id][1:]
        args = list(decoder.read(buffer) for decoder in decoders)
        return self._packet_factory.create(packet_id, *args)


class AddressData:

    from pyminehub.binutil import ByteData, ShortData, RawData

    _ip_version_data = ByteData()
    _ipv4_address_data = RawData(4)
    _port_data = ShortData()

    def read(self, data: bytearray) -> Address:
        ip_version = self._ip_version_data.read(data)
        ipv4_address = self._ipv4_address_data.read(data)
        port = self._port_data.read(data)
        return Address(ip_version, ipv4_address, port)

    def write(self, data: bytearray, value: Address) -> None:
        self._ip_version_data.write(data, value.ip_version)
        self._ipv4_address_data.write(data, value.address)
        self._port_data.write(data, value.port)


if __name__ == '__main__':
    from enum import Enum
    from pyminehub.binutil import *
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

    _data_converters = {
        ID.unconnected_pong: [
            ByteData(),
            LongData(),
            LongData(),
            MagicData(),
            StringData()
        ]
    }

    factory = PacketFactory(_packet_specs)
    codec = Codec(ID, factory, _data_converters)

    import doctest
    doctest.testmod()
