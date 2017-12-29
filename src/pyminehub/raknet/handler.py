from pyminehub.network.address import Address
from pyminehub.raknet.frame import Reliability


class SessionNotFound(Exception):

    def __init__(self, addr: Address) -> None:
        super().__init__(addr)

    @property
    def addr(self) -> Address:
        return self.args[0]


class GameDataHandler:

    def register_protocol(self, protocol) -> None:
        """The protocol object registers itself.

        Don't override and/or call this method.
        """
        # noinspection PyAttributeOutsideInit
        self._protocol = protocol

    def sendto(self, data: bytes, addr: Address, reliability: Reliability) -> None:
        """Send data to protocol object.

        Don't override this method. Other overridden methods call this method.

        :param data: sent data
        :param addr: the data is sent to the addr
        :param reliability: reliability of the sending
        """
        self._protocol.game_data_received(data, addr, reliability)

    def data_received(self, data: bytes, addr: Address) -> None:
        """Handle data.

        :param data: received data
        :param addr: data is sent from addr
        :raises SessionNotFound: if player session is lost (But, there may be something else to do)
        """
        raise NotImplementedError()

    def update(self) -> bool:
        """Update something of handler state.

        :return: return True, if there is nothing to do
        :raises SessionNotFound: if player session is lost (But, there may be something else to do)
        """
        raise NotImplementedError()

    def shutdown(self) -> None:
        raise NotImplementedError()
