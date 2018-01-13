from ipaddress import ip_address
from typing import NamedTuple

from pyminehub.config import ConfigKey, get_value

Address = tuple

AddressInPacket = NamedTuple('AddressInPacket', [('ip_version', int), ('address', bytes), ('port', int)])

_UNSPECIFIED_ADDRESSES = {
    4: '0.0.0.0',
    6: '::'
}


def get_unspecified_address() -> str:
    return _UNSPECIFIED_ADDRESSES[get_value(ConfigKey.IP_VERSION)]


def to_packet_format(addr: Address) -> AddressInPacket:
    ip_addr = ip_address(addr[0])
    return AddressInPacket(ip_addr.version, ip_addr.packed, addr[1])
