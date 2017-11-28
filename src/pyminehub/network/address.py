from typing import NamedTuple


IP_VERSION = 4


Address = NamedTuple('Address', [('ip_version', int), ('address', bytes), ('port', int)])


def to_address(addr: tuple) -> Address:
    return Address(IP_VERSION, bytes(int(v) for v in addr[0].split('.')), addr[1])
