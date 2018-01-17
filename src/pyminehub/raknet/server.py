import asyncio

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, get_unspecified_address, to_packet_format
from pyminehub.raknet.handler import SessionNotFound, GameDataHandler
from pyminehub.raknet.packet import RakNetPacketType, RakNetPacket, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session


class _RakNetServerProtocol(AbstractRakNetProtocol, asyncio.DatagramProtocol):

    def __init__(self, loop: asyncio.events.AbstractEventLoop, handler: GameDataHandler) -> None:
        self._sessions = {}  # TODO session timeout
        self._guid = get_value(ConfigKey.SERVER_GUID)
        self.server_id = 'MCPE;PyMineHub Server;160;1.2.7;0;20;{};{};{};'.format(
            get_value(ConfigKey.SERVER_GUID),
            get_value(ConfigKey.WORLD_NAME),
            get_value(ConfigKey.GAME_MODE).title()
        )
        super().__init__(loop, handler)

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
            RakNetPacketType.UNCONNECTED_PONG, packet.time_since_start, self._guid, True, self.server_id)
        self.send_to_remote(res_packet, addr)

    def _process_open_connection_request1(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY1, True, self._guid, False, packet.mtu_size)
        self.send_to_remote(res_packet, addr)

    def _process_open_connection_request2(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY2, True, self._guid, to_packet_format(addr), packet.mtu_size, False)
        self.send_to_remote(res_packet, addr)
        self._sessions[addr] = self.create_session(packet.mtu_size, addr)


def run(loop: asyncio.AbstractEventLoop, handler: GameDataHandler) -> None:
    server_address = (get_unspecified_address(), get_value(ConfigKey.SERVER_PORT))
    listen = loop.create_datagram_endpoint(
        lambda: _RakNetServerProtocol(loop, handler), local_addr=server_address)
    transport, protocol = loop.run_until_complete(listen)  # non-blocking
    try:
        loop.run_forever()  # blocking
    except KeyboardInterrupt:
        pass
    finally:
        handler.terminate()
        protocol.terminate()
        pending = asyncio.Task.all_tasks()
        try:
            loop.run_until_complete(asyncio.gather(*pending))
        except asyncio.CancelledError:
            pass
        finally:
            transport.close()


if __name__ == '__main__':
    class MockHandler(GameDataHandler):

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
