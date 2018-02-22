"""Frame (or Message)

This is called frame in http://wiki.vg/Pocket_Edition_Protocol_Documentation
and message in Wireshark and http://www.raknet.net/raknet/manual/systemoverview.html.

Attributes of each frame is named from name used by Wireshark.
"""

from pyminehub.value import ValueType, ValueObject, ValueObjectFactory

__all__ = [
    'RakNetFrame',
    'RakNetFrameType',
    'raknet_frame_factory'
]

RakNetFrame = ValueObject


class RakNetFrameType(ValueType):
    UNRELIABLE = 0x00
    RELIABLE = 0x40
    RELIABLE_ORDERED = 0x60
    RELIABLE_ORDERED_HAS_SPLIT = 0x70


_raknet_frame_specs = {
    RakNetFrameType.UNRELIABLE: [
        ('type', RakNetFrameType),
        ('payload_length', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE: [
        ('type', RakNetFrameType),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE_ORDERED: [
        ('type', RakNetFrameType),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('payload', bytes)
    ],
    RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: [
        ('type', RakNetFrameType),
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


raknet_frame_factory = ValueObjectFactory(globals(), _raknet_frame_specs, 'Frame')
