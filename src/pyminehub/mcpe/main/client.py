from pyminehub.mcpe.network import MCPEClient
from pyminehub.raknet import ClientConnection


def connect(server_host: str, port: int=None) -> ClientConnection[MCPEClient]:
    """Connect to PyMineHub server.

    :param server_host: IP address that PyMineHub server listen
    :param port: port number that PyMineHub server listen
    """
    from pyminehub.raknet import connect_raknet
    return connect_raknet(MCPEClient(), server_host, port)


if __name__ == '__main__':
    from pyminehub.mcpe.network import MCPEClient
    with connect('127.0.0.1') as client:  # type: MCPEClient
        client.execute_command('/about 1')
        print(client.wait_response())
