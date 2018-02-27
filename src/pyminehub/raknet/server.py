import asyncio

from pyminehub.config import ConfigKey, get_value
from pyminehub.network.address import Address, get_unspecified_address, to_packet_format
from pyminehub.network.handler import GameDataHandler, SessionNotFound
from pyminehub.network.server import Server
from pyminehub.raknet.packet import RakNetPacketType, RakNetPacket, raknet_packet_factory
from pyminehub.raknet.protocol import AbstractRakNetProtocol
from pyminehub.raknet.session import Session

__all__ = [
    'raknet_server'
]


class _RakNetServerProtocol(AbstractRakNetProtocol, asyncio.DatagramProtocol):

    def __init__(self, handler: GameDataHandler) -> None:
        super().__init__(handler)
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

    def remove_session(self, addr: Address) -> bool:
        if addr in self._sessions:
            self._sessions[addr].close()
            del self._sessions[addr]
            return True
        else:
            return False

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
        if addr in self._sessions and self._sessions[addr].is_closed:
            return  # wait for session closing
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY1, True, self.guid, False, packet.mtu_size)
        self.send_to_remote(res_packet, addr)
        if addr not in self._sessions:
            self._sessions[addr] = self.create_session(packet.mtu_size, addr)
        else:
            assert not self._sessions[addr].is_closed

    def _process_open_connection_request2(self, packet: RakNetPacket, addr: Address) -> None:
        res_packet = raknet_packet_factory.create(
            RakNetPacketType.OPEN_CONNECTION_REPLY2, True, self.guid, to_packet_format(addr), packet.mtu_size, False)
        self.send_to_remote(res_packet, addr)
        self._sessions[addr].reset(packet.mtu_size)


class _RakNetServer(Server):

    def __init__(self, handler: GameDataHandler, server_address: Address) -> None:
        self._handler = handler
        self._server_address = server_address
        self._transport = None
        self._protocol = None

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(
            lambda: _RakNetServerProtocol(self._handler), local_addr=self._server_address)
        self._transport, self._protocol = loop.run_until_complete(listen)  # non-blocking

    def terminate(self) -> None:
        self._protocol.terminate()

    async def close(self) -> None:
        self._transport.close()

    def remove_session(self, addr: Address) -> bool:
        return self._protocol.remove_session(addr)


def raknet_server(handler: GameDataHandler) -> Server:
    server_address = (get_unspecified_address(), get_value(ConfigKey.RAKNET_SERVER_PORT))
    return _RakNetServer(handler, server_address)


if __name__ == '__main__':
    from typing import Optional
    from pyminehub.network.handler import Protocol

    class MockHandler(GameDataHandler):

        def __init__(self) -> None:
            self._protocol = None

        @property
        def guid(self) -> int:
            return 0

        def register_protocol(self, protocol: Protocol, addr: Optional[Address] = None) -> None:
            self._protocol = protocol

        def remove_protocol(self, addr: Address) -> None:
            pass

        # noinspection PyUnusedLocal
        def get_protocol(self, addr: Address) -> Protocol:
            return self._protocol

        def data_received(self, data: bytes, addr: Address) -> None:
            print('{} {}'.format(addr, data.hex()))

        async def update(self) -> None:
            await asyncio.sleep(1)

        def disconnect(self, addr: Address) -> None:
            pass

        def terminate(self) -> None:
            pass

    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = raknet_server(MockHandler())
    server.start()
    _loop = asyncio.get_event_loop()
    try:
        _loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.terminate()
        pending = asyncio.Task.all_tasks()
        try:
            _loop.run_until_complete(asyncio.gather(*pending))
        except asyncio.CancelledError:
            pass
        finally:
            async def close():
                server.close()
            _loop.run_until_complete(close())  # sock.close() is called with loop.call_soon()
    _loop.close()
