import asyncio
from logging import getLogger
from random import randrange
from typing import Optional, TypeVar

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet.handler import GameDataHandler, SessionNotFound
from pyminehub.raknet.packet import RakNetPacket, RakNetPacketType, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session

_logger = getLogger(__name__)


_RAKNET_PROTOCOL_VERSION = 8


class RakNetClientProtocol(AbstractRakNetProtocol, asyncio.DatagramProtocol):

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            handler: GameDataHandler,
            is_internal_loop: bool
    ) -> None:
        self._session = None  # type: Session
        self._guid = randrange(1 << (8 * 8))  # long range
        super().__init__(loop, handler, is_internal_loop)

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

    def connect_raknet(self, addr: Address) -> None:
        # TODO change mtu_size to dynamic
        send_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REQUEST1, True, _RAKNET_PROTOCOL_VERSION, 1492)
        self.send_to_remote(send_packet, addr)

        # wait

    def _process_open_connection_reply1(self, packet: RakNetPacket, addr: Address) -> None:
        send_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REQUEST2, True, to_packet_format(addr), packet.mtu_size, self._guid)
        self.send_to_remote(send_packet, addr)

    def _process_open_connection_reply2(self, packet: RakNetPacket, addr: Address) -> None:
        self._session = self.create_session(packet.mtu_size, addr)


class AbstractClient(GameDataHandler):

    def data_received(self, data: bytes, addr: Address) -> None:
        raise NotImplementedError()

    async def update(self) -> None:
        raise NotImplementedError()

    # noinspection PyAttributeOutsideInit
    def connect(self, server_addr: Address, transport: asyncio.Transport, protocol: RakNetClientProtocol):
        self.__transport = transport
        self.__protocol = protocol
        self.__protocol.connect_raknet(server_addr)

    def terminate(self) -> None:
        self.__protocol.terminate()
        self.__transport.close()


Client = TypeVar('Client', bound=AbstractClient)


class ClientConnection:

    def __init__(
            self,
            client: Client,
            server_addr: Address,
            loop: Optional[asyncio.AbstractEventLoop]=None
    ) -> None:
        internal_loop = asyncio.get_event_loop() if loop is None else loop
        self._client = client
        self._server_addr = server_addr
        self._loop = internal_loop
        self._is_internal_loop = internal_loop != loop

    def __enter__(self) -> Client:
        connect = self._loop.create_datagram_endpoint(
            lambda: RakNetClientProtocol(self._loop, self._client, self._is_internal_loop),
            remote_addr=self._server_addr)
        transport, protocol = self._loop.run_until_complete(connect)
        self._client.connect(self._server_addr, transport, protocol)
        return self._client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._is_internal_loop:
            pending = asyncio.Task.all_tasks()
            try:
                self._loop.run_until_complete(asyncio.gather(*pending))
            except asyncio.CancelledError:
                pass
        self._client.terminate()


def connect_raknet(
        client: Client,
        server_host: str,
        port: Optional[int]=None,
        loop: Optional[asyncio.AbstractEventLoop]=None
) -> ClientConnection:
    server_address = (server_host, get_value(ConfigKey.SERVER_PORT) if port is None else port)
    return ClientConnection(client, server_address, loop)


if __name__ == '__main__':
    class MockClient(AbstractClient):

        def data_received(self, data: bytes, addr: Address) -> None:
            print('{} {}'.format(addr, data.hex()))

        async def update(self) -> None:
            await asyncio.sleep(1)

    import logging
    logging.basicConfig(level=logging.DEBUG)
    with connect_raknet(MockClient(), '127.0.0.1') as _client:
        pass
