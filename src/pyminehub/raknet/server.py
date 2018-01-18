import asyncio

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, get_unspecified_address, to_packet_format
from pyminehub.raknet.handler import SessionNotFound, GameDataHandler
from pyminehub.raknet.packet import RakNetPacketType, RakNetPacket, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session


class _RakNetServerProtocol(AbstractRakNetProtocol, asyncio.DatagramProtocol):

    def __init__(self, loop: asyncio.events.AbstractEventLoop, handler: GameDataHandler) -> None:
        super().__init__(loop, handler)
        self._sessions = {}  # TODO session timeout
        self.server_id = 'MCPE;PyMineHub Server;160;1.2.7;0;20;{};{};{};'.format(
            self.guid,
            get_value(ConfigKey.WORLD_NAME),
            get_value(ConfigKey.GAME_MODE).title()
        )

    def terminate(self) -> None:
        super().terminate()
        for session in self._sessions.values():
            session.close()

    def remove_session(self, addr: Address) -> None:
        if addr in self._sessions:
            self._sessions[addr].close()
            del self._sessions[addr]

    def get_session(self, addr: Address) -> Session:
        try:
            return self._sessions[addr]
        except KeyError:
            raise SessionNotFound(addr)

    def _process_unconnected_ping(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.UNCONNECTED_PONG, packet.time_since_start, self.guid, True, self.server_id)
        self.send_to_remote(res_packet, addr)

    def _process_open_connection_request1(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY1, True, self.guid, False, packet.mtu_size)
        self.send_to_remote(res_packet, addr)

    def _process_open_connection_request2(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY2, True, self.guid, to_packet_format(addr), packet.mtu_size, False)
        self.send_to_remote(res_packet, addr)
        self._sessions[addr] = self.create_session(packet.mtu_size, addr)


class ServerProcess:

    def __init__(self, loop: asyncio.AbstractEventLoop, handler: GameDataHandler, server_address: Address) -> None:
        self._loop = loop
        self._handler = handler
        self._server_address = server_address
        self._transport = None
        self._protocol = None
        self._stopped = False

    def __enter__(self) -> 'ServerProcess':
        listen = self._loop.create_datagram_endpoint(
            lambda: _RakNetServerProtocol(self._loop, self._handler), local_addr=self._server_address)
        self._transport, self._protocol = self._loop.run_until_complete(listen)  # non-blocking
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None and not self._stopped:
                self._loop.run_forever()  # blocking
        except KeyboardInterrupt:
            pass
        finally:
            self._handler.terminate()
            self._protocol.terminate()
            pending = asyncio.Task.all_tasks()
            try:
                self._loop.run_until_complete(asyncio.gather(*pending))
            except asyncio.CancelledError:
                pass
            finally:
                self._transport.close()

    def start(self) -> None:
        self.__enter__()

    def join(self) -> None:
        self.__exit__(None, None, None)

    def stop(self) -> None:
        self._stopped = True
        for task in asyncio.Task.all_tasks(self._loop):
            task.cancel()


def run(loop: asyncio.AbstractEventLoop, handler: GameDataHandler) -> ServerProcess:
    server_address = (get_unspecified_address(), get_value(ConfigKey.SERVER_PORT))
    return ServerProcess(loop, handler, server_address)


if __name__ == '__main__':
    class MockHandler(GameDataHandler):

        @property
        def guid(self) -> int:
            return 0

        def data_received(self, data: bytes, addr: Address) -> None:
            print('{} {}'.format(addr, data.hex()))

        async def update(self) -> None:
            await asyncio.sleep(1)

        def terminate(self) -> None:
            pass

    import logging
    logging.basicConfig(level=logging.DEBUG)
    _loop = asyncio.get_event_loop()
    run(_loop, MockHandler())
    _loop.close()
