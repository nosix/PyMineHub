import asyncio

from pyminehub.raknet import ClientConnection


def connect(server_host: str, port: int=None, loop: asyncio.AbstractEventLoop=None) -> ClientConnection:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    :param loop: client run on this loop
    """
    from pyminehub.raknet import connect_raknet
    from pyminehub.mcpe.network import MCPEClient
    return connect_raknet(MCPEClient(), server_host, port, loop)


if __name__ == '__main__':
    from pyminehub.mcpe.network import MCPEClient
    with connect('127.0.0.1') as client:  # type: MCPEClient
        client.execute_command('/about 1')
        print(client.wait_response())
