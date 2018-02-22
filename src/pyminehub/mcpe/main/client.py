from typing import Callable, TypeVar

from pyminehub.mcpe.network import MCPEClient
from pyminehub.network.client import ClientConnection

__all__ = [
    'connect',
    'Client'
]


Client = TypeVar('Client', bound=MCPEClient)


def connect(
        server_host: str,
        port: int=None,
        raknet=False,
        timeout: float=0,
        player_name: str='',
        locale: str='ja_JP',
        client_factory: Callable[[str, str], Client]=MCPEClient
) -> ClientConnection[Client]:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    :param raknet: True to use RakNet protocol
    :param timeout: seconds to wait for a connection with the server (0 means no timeout)
    :param player_name: if player name is empty string then player is invisible
    :param locale: locale in application
    :param client_factory: generate Client instance
    """
    if raknet:
        from pyminehub.raknet import connect_raknet as connect_server
    else:
        from pyminehub.tcp import connect_tcp as connect_server
    return connect_server(client_factory(player_name, locale), server_host, port, timeout)


if __name__ == '__main__':
    with connect('127.0.0.1') as client:  # type: MCPEClient
        client.execute_command('/about 1')
        client.wait_response(1)
        print(client.next_message())
