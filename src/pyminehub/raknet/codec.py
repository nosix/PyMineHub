from pyminehub.binutil import *
from pyminehub.network.codec import Codec
from pyminehub.raknet.encapsulation import CapsuleID, capsule_factory
from pyminehub.raknet.packet import PacketID, packet_factory


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
_null_padding = ValueFilter(_raw_data, read=lambda data: len(data), write=lambda value: b'0' * value)
_bool_data = ValueFilter(_byte_data, read=lambda data: data != 0, write=lambda value: 1 if value else 0)
_false_data = ValueFilter(_byte_data, read=lambda data: data != 0, write=_filter_false)


_packet_converters = {
    PacketID.unconnected_ping: [
        _byte_data,
        _long_data,
        _magic_data,
        _long_data
    ],
    PacketID.unconnected_pong: [
        _byte_data,
        _long_data,
        _long_data,
        _magic_data,
        _string_data
    ],
    PacketID.open_connection_request1: [
        _byte_data,
        _magic_data,
        _byte_data,
        _null_padding
    ],
    PacketID.open_connection_reply1: [
        _byte_data,
        _magic_data,
        _long_data,
        _false_data,
        _short_data
    ],
    PacketID.open_connection_request2: [
        _byte_data,
        _magic_data,
        _byte_data,
        _4bytes_data,
        _short_data,
        _short_data,
        _long_data
    ],
    PacketID.open_connection_reply2: [
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
    _packet_converters[PacketID['custom_packet_{:x}'.format(n)]] = [
        _byte_data,
        _triad_data,
        _raw_data
    ]


for packet_id in (PacketID.nck, PacketID.ack):
    _packet_converters[packet_id] = [
        _byte_data,
        _short_data,
        _bool_data,
        _triad_data,
        _triad_data
    ]


_capsule_converters = {
    CapsuleID.reliable: [
        _byte_data,
        _short_data,
        _triad_data,
        _raw_data
    ]
}


packet_codec = Codec(PacketID, packet_factory, _packet_converters)
capsule_codec = Codec(CapsuleID, capsule_factory, _capsule_converters)
