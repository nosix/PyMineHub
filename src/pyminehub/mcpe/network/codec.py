from pyminehub.binutil import *
from pyminehub.mcpe.network.packet import PacketID, packet_factory
from pyminehub.network.codec import Codec


def _filter_false(value: bool) -> int:
    assert not value
    return 0


_byte_data = ByteData()
_long_data = LongData()

_false_data = ValueFilter(_byte_data, read=lambda value: value != 0, write=_filter_false)


_packet_converters = {
    PacketID.connection_request: [
        _byte_data,
        _long_data,
        _long_data,
        _false_data
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
