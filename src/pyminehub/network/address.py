from typing import NamedTuple


IP_VERSION = 4

Address = tuple

AddressInPacket = NamedTuple('Address', [('ip_version', int), ('address', bytes), ('port', int)])


def to_packet_format(addr: Address) -> AddressInPacket:
    return AddressInPacket(IP_VERSION, bytes(int(v) for v in addr[0].split('.')), addr[1])
