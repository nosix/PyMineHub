import asyncio
from logging import getLogger
from typing import Generic, Optional, TypeVar

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet.handler import GameDataHandler, SessionNotFound
from pyminehub.raknet.packet import RakNetPacket, RakNetPacketType, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session

__all__ = [
    'AbstractClient',
    'Client',
    'ClientConnection',
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

    def remove_session(self, addr: Address) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None

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


class AbstractClient:

    @property
    def handler(self) -> GameDataHandler:
        raise NotImplementedError()

    @property
    def server_addr(self) -> Address:
        return self.__server_addr

    async def start(self) -> None:
        """Start client

        This method is called when connection started.
        """
        raise NotImplementedError()

    async def finished(self) -> None:
        """Callback when client finish

        This method is called when client finish.
        """
        raise NotImplementedError()

    # noinspection PyAttributeOutsideInit
    async def connect(self, server_addr: Address, transport: asyncio.Transport, protocol: _RakNetClientProtocol) -> None:
        """Connect RakNet server

        Don't override this method.
        """
        self.__server_addr = server_addr
        self.__transport = transport
        self.__protocol = protocol
        await self.__protocol.connect_raknet(server_addr)
        await self.start()

    async def terminate(self) -> None:
        """Terminate connection

        Call this method if this method is overridden.
        """
        await self.finished()
        self.__protocol.terminate()
        self.__transport.close()


Client = TypeVar('Client', bound=AbstractClient)


class ClientConnection(Generic[Client]):

    def __init__(
            self,
            client: Client,
            server_addr: Address,
            timeout: float
    ) -> None:
        self._client = client
        self._server_addr = server_addr
        self._timeout = timeout

    def __enter__(self) -> Client:
        loop = asyncio.get_event_loop()
        endpoint = loop.create_datagram_endpoint(
            lambda: _RakNetClientProtocol(self._client.handler),
            remote_addr=self._server_addr)
        transport, protocol = loop.run_until_complete(endpoint)
        connect = self._client.connect(self._server_addr, transport, protocol)
        if self._timeout > 0:
            connect = asyncio.ensure_future(connect)
            asyncio.ensure_future(self._wait_timeout(connect))
        loop.run_until_complete(connect)
        # noinspection PyTypeChecker
        return self._client  # FIXME why is type check fail?

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._client.terminate())

    def start(self) -> Client:
        # noinspection PyTypeChecker
        return self.__enter__()  # FIXME why is type check fail?

    def close(self) -> None:
        self.__exit__(None, None, None)

    async def _wait_timeout(self, future: asyncio.Future):
        await asyncio.sleep(self._timeout)
        future.cancel()
        _logger.info('timeout to connect server')


def connect_raknet(
        client: Client,
        server_host: str,
        port: Optional[int]=None,
        timeout: float=0
) -> ClientConnection[Client]:
    server_address = (server_host, get_value(ConfigKey.SERVER_PORT) if port is None else port)
    return ClientConnection(client, server_address, timeout)


if __name__ == '__main__':
    class MockHandler(GameDataHandler):

        @property
        def guid(self) -> int:
            return 0

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

        async def start(self) -> None:
            print('Client session started.')

        async def finished(self) -> None:
            print('Client session finished.')

    import logging
    logging.basicConfig(level=logging.DEBUG)
    with connect_raknet(MockClient(), '127.0.0.1') as _client:
        pass
