import asyncio
from logging import getLogger
from typing import Optional

from pyminehub.network.address import Address
from pyminehub.network.client import Client, ClientConnection
from pyminehub.network.handler import GameDataHandler
from pyminehub.tcp.protocol import TcpProtocol

_logger = getLogger(__name__)


class _TcpClientProtocol(TcpProtocol):

    pass


class _TcpClientConnection(ClientConnection):

    def __init__(
            self,
            client: Client,
            server_addr: Address,
            timeout: float
    ) -> None:
        self._client = client
        self._server_addr = server_addr
        self._timeout = timeout
        self._connection = None

    def __enter__(self) -> Client:
        host, port = self._server_addr
        loop = asyncio.get_event_loop()
        self._connection = loop.create_connection(
            lambda: _TcpClientProtocol(self._client.handler), host=host, port=port)
        loop.run_until_complete(self._connection)
        connect = self._connect()
        if self._timeout > 0:
            connect = asyncio.ensure_future(connect)
            asyncio.ensure_future(self._wait_timeout(connect))
        loop.run_until_complete(connect)
        # noinspection PyTypeChecker
        return self._client  # FIXME why is type check fail?

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._terminate())

    async def _wait_timeout(self, future: asyncio.Future):
        await asyncio.sleep(self._timeout)
        future.cancel()
        _logger.info('timeout to connect server')

    async def _connect(self) -> None:
        await self._client.start(self._server_addr)

    async def _terminate(self) -> None:
        await self._client.finished()
        self._connection.close()


def connect_tcp(
        client: Client,
        server_host: str,
        port: Optional[int]=None,
        timeout: float=0
) -> ClientConnection[Client]:
    server_address = (server_host, 19232 if port is None else port)
    return _TcpClientConnection(client, server_address, timeout)


if __name__ == '__main__':
    from pyminehub.network.client import AbstractClient
    from pyminehub.network.handler import Protocol

    class MockHandler(GameDataHandler):

        @property
        def guid(self) -> int:
            return 0

        def register_protocol(self, protocol: Protocol, addr: Optional[Address] = None) -> None:
            pass

        def remove_protocol(self, addr: Address) -> None:
            pass

        def get_protocol(self, addr: Address) -> Protocol:
            pass

        def data_received(self, data: bytes, addr: Address) -> None:
            print('{} {}'.format(addr, data.hex()))

        async def update(self) -> None:
            await asyncio.Event().wait()

        def terminate(self) -> None:
            pass

    class MockClient(AbstractClient):

        def __init__(self) -> None:
            self._handler = MockHandler()

        @property
        def handler(self) -> GameDataHandler:
            return self._handler

        async def start(self, server_addr: Address) -> None:
            print('Client session started.')

        async def finished(self) -> None:
            print('Client session finished.')

    import logging
    logging.basicConfig(level=logging.DEBUG)
    with connect_tcp(MockClient(), '127.0.0.1') as _client:
        pass
