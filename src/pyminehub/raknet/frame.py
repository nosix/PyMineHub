from typing import NamedTuple as _NamedTuple, Optional

from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

Reliability = _NamedTuple('Reliability', [('reliable', bool), ('channel', Optional[int])])

RakNetFrame = ValueObject


class RakNetFrameType(ValueType):
    UNRELIABLE = 0x00
    RELIABLE = 0x40
    RELIABLE_ORDERED = 0x60
    RELIABLE_ORDERED_HAS_SPLIT = 0x70


_raknet_frame_specs = {
    RakNetFrameType.UNRELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE_ORDERED: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: [
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


raknet_frame_factory = ValueObjectFactory(_raknet_frame_specs)
