from typing import Optional, NamedTuple

from pyminehub.network.address import Address

__all__ = [
    'GameDataHandler',
    'Protocol',
    'SessionNotFound',
    'Reliability'
]


Reliability = NamedTuple('Reliability', [('reliable', bool), ('channel', Optional[int])])


class SessionNotFound(Exception):

    def __init__(self, addr: Optional[Address]=None) -> None:
        super().__init__(addr)

    @property
    def addr(self) -> Optional[Address]:
        return self.args[0]


class Protocol:

    def game_data_received(self, data: bytes, addr: Address, reliability: Reliability) -> None:
        raise NotImplementedError()


class GameDataHandler:

    @property
    def guid(self) -> int:
        """Return long (64 bits int) value."""
        raise NotImplementedError()

    def register_protocol(self, protocol: Protocol, addr: Optional[Address]=None) -> None:
        """Register the protocol used for communication with the specified address

        :param protocol: registered protocol (register as default if addr is None)
        :param addr: communication destination
        """
        raise NotImplementedError()

    def remove_protocol(self, addr: Address) -> None:
        raise NotImplementedError()

    def data_received(self, data: bytes, addr: Address) -> None:
        """Handle data.

        :param data: received data
        :param addr: data is sent from addr
        :raises SessionNotFound: if player session is lost (But, there may be something else to do)
        """
        raise NotImplementedError()

    async def update(self) -> None:
        """Update something of handler state.

        :raises SessionNotFound: if player session is lost (But, there may be something else to do)
        """
        raise NotImplementedError()

    def terminate(self) -> None:
        raise NotImplementedError()
