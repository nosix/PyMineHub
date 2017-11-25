from enum import Enum

from pyminehub.network.packet import PacketFactory


class CapsuleID(Enum):
    capsule_00 = 0x00
    capsule_40 = 0x40
    capsule_60 = 0x60


_capsule_specs = {
    CapsuleID.capsule_40: [
        ('id', int),
        ('length', int),
        ('count', int),
        ('payload', bytes)
    ]
}


capsule_factory = PacketFactory(_capsule_specs)
