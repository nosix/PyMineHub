from typing import Callable, TypeVar

from pyminehub.mcpe.network import MCPEClient
from pyminehub.raknet import ClientConnection

__all__ = [
    'connect'
]


Client = TypeVar('Client', bound=MCPEClient)


def connect(
        server_host: str,
        port: int=None,
        player_name: str='',
        locale: str='ja_JP',
        client_factory: Callable[[str, str], Client]=MCPEClient
) -> ClientConnection[Client]:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    :param player_name: if player name is empty string then player is invisible
    :param locale: locale in application
    :param client_factory: generate Client instance
    """
    from pyminehub.raknet import connect_raknet
    return connect_raknet(client_factory(player_name, locale), server_host, port)


if __name__ == '__main__':
    with connect('127.0.0.1') as client:  # type: MCPEClient
        client.execute_command('/about 1')
        client.wait_response(1)
        print(client.next_message())
