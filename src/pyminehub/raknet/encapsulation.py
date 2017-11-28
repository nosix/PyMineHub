from enum import Enum

from pyminehub.network.packet import PacketFactory


class CapsuleID(Enum):
    unreliable = 0x00
    reliable = 0x40
    reliable_ordered = 0x60


_capsule_specs = {
    CapsuleID.reliable: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('payload', bytes)
    ],
    CapsuleID.reliable_ordered: [
        ('id', int),
        ('payload_length', int),
        ('reliable_message_num', int),
        ('message_ordering_index', int),
        ('message_ordering_chanel', int),
        ('payload', bytes)
    ]
}


capsule_factory = PacketFactory(_capsule_specs)
