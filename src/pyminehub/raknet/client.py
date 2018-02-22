import asyncio
from logging import getLogger
from typing import Optional

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, to_packet_format
from pyminehub.network.client import Client, ClientConnection
from pyminehub.network.handler import GameDataHandler, SessionNotFound
from pyminehub.raknet.packet import RakNetPacket, RakNetPacketType, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session

__all__ = [
    'connect_raknet'
]


_logger = getLogger(__name__)


_RAKNET_PROTOCOL_VERSION = 8


class _RakNetClientProtocol(AbstractRakNetProtocol, asyncio.DatagramProtocol):

    def __init__(
            self,
            handler: GameDataHandler
    ) -> None:
        self._session = None  # type: Session
        self._connected = asyncio.Event()
        super().__init__(handler)

    def terminate(self) -> None:
        super().terminate()
        if self._session is not None:
            self._session.close()

    def remove_session(self, addr: Address) -> bool:
        if self._session is not None:
            self._session.close()
            self._session = None
            return True
        else:
            return False

    def get_session(self, addr: Address) -> Session:
        if self._session is not None:
            return self._session
        else:
            raise SessionNotFound(addr)

    async def connect_raknet(self, addr: Address) -> None:
        # TODO change mtu_size to dynamic
        send_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REQUEST1, True, _RAKNET_PROTOCOL_VERSION, 1492)
        self.send_to_remote(send_packet, addr)
        await self._connected.wait()

    def _process_open_connection_reply1(self, packet: RakNetPacket, addr: Address) -> None:
        send_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REQUEST2, True, to_packet_format(addr), packet.mtu_size, self.guid)
        self.send_to_remote(send_packet, addr)

    def _process_open_connection_reply2(self, packet: RakNetPacket, addr: Address) -> None:
        self._session = self.create_session(packet.mtu_size, addr)
        self._connected.set()


class _RakNetClientConnection(ClientConnection):

    def __init__(
            self,
            client: Client,
            server_addr: Address,
            timeout: float
    ) -> None:
        self._client = client
        self._server_addr = server_addr
        self._timeout = timeout
        self._transport = None
        self._protocol = None

    def __enter__(self) -> Client:
        loop = asyncio.get_event_loop()
        endpoint = loop.create_datagram_endpoint(
            lambda: _RakNetClientProtocol(self._client.handler), remote_addr=self._server_addr)
        self._transport, self._protocol = loop.run_until_complete(endpoint)
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
        await self._protocol.connect_raknet(self._server_addr)
        await self._client.start(self._server_addr)

    async def _terminate(self) -> None:
        await self._client.finished()
        self._protocol.terminate()
        self._transport.close()


def connect_raknet(
        client: Client,
        server_host: str,
        port: Optional[int]=None,
        timeout: float=0
) -> ClientConnection[Client]:
    server_address = (server_host, get_value(ConfigKey.SERVER_PORT) if port is None else port)
    return _RakNetClientConnection(client, server_address, timeout)


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
    with connect_raknet(MockClient(), '127.0.0.1') as _client:
        pass
