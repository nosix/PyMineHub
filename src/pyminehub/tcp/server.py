import asyncio
from typing import Dict

from pyminehub.network.address import Address
from pyminehub.network.handler import GameDataHandler
from pyminehub.network.server import Server
from pyminehub.tcp.protocol import TcpProtocol

__all__ = [
    'tcp_server'
]


class _TcpServerProtocol(TcpProtocol):

    def __init__(self, handler: GameDataHandler, sessions: Dict[Address, asyncio.Transport]) -> None:
        super().__init__(handler)
        self._sessions = sessions

    # asyncio.Protocol methods

    def connection_made(self, transport: asyncio.Transport) -> None:
        super().connection_made(transport)
        self._sessions[self.destination_address] = transport

    def connection_lost(self, exc: Exception) -> None:
        super().connection_lost(exc)
        del self._sessions[self.destination_address]


class _TcpServer(Server):

    def __init__(self, handler: GameDataHandler, server_addr: Address) -> None:
        self._handler = handler
        self._server_address = server_addr
        self._server = None
        self._sessions = {}  # type: Dict[Address, asyncio.Transport]

    def start(self) -> None:
        host, port = self._server_address
        loop = asyncio.get_event_loop()
        listen = loop.create_server(
            lambda: _TcpServerProtocol(self._handler, self._sessions), host=host, port=port)
        self._server = loop.run_until_complete(listen)

    def terminate(self) -> None:
        self._server.close()

    async def close(self) -> None:
        await self._server.wait_closed()

    def remove_session(self, addr: Address) -> bool:
        if addr in self._sessions:
            del self._sessions[addr]
            return True
        else:
            return False


def tcp_server(handler: GameDataHandler) -> Server:
    server_address = ('127.0.0.1', 19232)
    return _TcpServer(handler, server_address)
