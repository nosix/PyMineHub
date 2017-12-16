from typing import NamedTuple as _NamedTuple, Optional

from pyminehub.network.packet import PacketID, PacketFactory

Reliability = _NamedTuple('Reliability', [('reliable', bool), ('channel', Optional[int])])


class RakNetFrameID(PacketID):
    UNRELIABLE = 0x00
    RELIABLE = 0x40
    RELIABLE_ORDERED = 0x60
    RELIABLE_ORDERED_HAS_SPLIT = 0x70


_frame_specs = {
    RakNetFrameID.UNRELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('payload', bytes)
    ],
    RakNetFrameID.RELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('payload', bytes)
    ],
    RakNetFrameID.RELIABLE_ORDERED: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('payload', bytes)
    ],
    RakNetFrameID.RELIABLE_ORDERED_HAS_SPLIT: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('split_packet_count', int),
        ('split_packet_id', int),
        ('split_packet_index', int),
        ('payload', bytes)
    ]
}


raknet_frame_factory = PacketFactory(_frame_specs)
