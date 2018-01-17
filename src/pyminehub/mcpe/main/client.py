import asyncio

from pyminehub.network.address import Address
from pyminehub.raknet import ClientConnection, connect_raknet, AbstractClient


class MockClient(AbstractClient):

    def data_received(self, data: bytes, addr: Address) -> None:
        pass

    def update(self) -> None:
        pass


def connect(server_host: str, port: int=None, loop: asyncio.AbstractEventLoop=None) -> ClientConnection:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    :param loop: client run on this loop
    """
    return connect_raknet(MockClient(), server_host, port, loop)  # TODO implement


if __name__ == '__main__':
    with connect('127.0.0.1') as client:
        pass
