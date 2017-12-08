from enum import Enum

from pyminehub.network.packet import PacketFactory


class CapsuleID(Enum):
    UNRELIABLE = 0x00
    RELIABLE = 0x40
    RELIABLE_ORDERED = 0x60
    RELIABLE_ORDERED_HAS_SPLIT = 0x70


_capsule_specs = {
    CapsuleID.UNRELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('payload', bytes)
    ],
    CapsuleID.RELIABLE: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('payload', bytes)
    ],
    CapsuleID.RELIABLE_ORDERED: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('payload', bytes)
    ],
    CapsuleID.RELIABLE_ORDERED_HAS_SPLIT: [
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


capsule_factory = PacketFactory(_capsule_specs)
