import asyncio
from collections import namedtuple
from logging import getLogger, basicConfig

from pyminehub.network.address import IP_VERSION, to_address
from pyminehub.network.codec import PacketCodecContext
from pyminehub.raknet.codec import packet_codec, capsule_codec
from pyminehub.raknet.packet import PacketID, packet_factory
from pyminehub.raknet.session import Session

_logger = getLogger(__name__)


class GameDataHandler:

    def register_protocol(self, protocol):
        # noinspection PyAttributeOutsideInit
        self._protocol = protocol

    def sendto(self, data: bytes, addr: tuple) -> None:
        self._protocol.game_data_received(data, addr)

    def data_received(self, data: bytes, addr: tuple) -> None:
        raise NotImplementedError()


class _RakNetServerProtocol(asyncio.DatagramProtocol):

    def __init__(self, loop: asyncio.events.AbstractEventLoop, handler: GameDataHandler):
        handler.register_protocol(self)
        self._loop = loop
        self._handler = handler
        self._sessions = {}  # TODO session timeout
        self.guid = 472877960873915066
        self.server_id = 'MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'

    def game_data_received(self, data: bytes, addr: tuple) -> None:
        session = self._sessions[addr]
        session.send_custom_packet(data)

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        # noinspection PyAttributeOutsideInit
        self._transport = transport

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + PacketID(packet.id).name)(packet, addr)

    def connection_lost(self, exc: Exception):
        _logger.exception('RakNet connection lost', exc_info=exc)
        self._loop.stop()

    def send_to_client(self, packet: namedtuple, addr: tuple) -> None:
        _logger.debug('< %s %s', addr, packet)
        self._transport.sendto(packet_codec.encode(packet), addr)

    def send_ack_and_nck(self) -> None:
        for addr, session in self._sessions.items():
            def sendto(res_packet):
                self.send_to_client(res_packet, addr)
            session.send_ack_and_nck(sendto)

    def _process_unconnected_ping(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.UNCONNECTED_PONG, packet.time_since_start, self.guid, True, self.server_id)
        self.send_to_client(res_packet, addr)

    def _process_open_connection_request1(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.OPEN_CONNECTION_REPLY1, True, self.guid, False, packet.mtu_size)
        self.send_to_client(res_packet, addr)

    def _process_open_connection_request2(self, packet: namedtuple, addr: tuple) -> None:
        assert packet.server_address.ip_version == IP_VERSION
        res_packet = packet_factory.create(
            PacketID.OPEN_CONNECTION_REPLY2, True, self.guid, to_address(addr), packet.mtu_size, False)
        self.send_to_client(res_packet, addr)
        self._sessions[addr] = Session(
            lambda _data: self._handler.data_received(_data, addr),
            lambda _packet: self.send_to_client(_packet, addr))

    def _process_custom_packet(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        context = PacketCodecContext()
        capsules = []
        length = 0
        while length < len(packet.payload):
            payload = packet.payload[length:]
            _logger.debug('%s', payload.hex())
            capsules.append(capsule_codec.decode(payload, context))
            length += context.length
            context.clear()
        session.capsule_received(packet.packet_sequence_num, capsules)

    def _process_custom_packet_4(self, packet: namedtuple, addr: tuple) -> None:
        self._process_custom_packet(packet, addr)

    def _process_custom_packet_c(self, packet: namedtuple, addr: tuple) -> None:
        self._process_custom_packet(packet, addr)

    def _process_nck(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        session.nck_received(packet)

    def _process_ack(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        session.ack_received(packet)


async def _send(protocol: _RakNetServerProtocol):
    while True:
        await asyncio.sleep(0.1)
        protocol.send_ack_and_nck()


def run(handler, log_level=None):
    not log_level or basicConfig(level=log_level)
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        lambda: _RakNetServerProtocol(loop, handler), local_addr=('0.0.0.0', 19132))
    transport, protocol = loop.run_until_complete(listen)
    try:
        loop.run_until_complete(_send(protocol))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()
        loop.close()


if __name__ == '__main__':
    import logging

    class MockHandler(GameDataHandler):
        def data_received(self, data: bytes, addr: tuple) -> None:
            print('{} {}'.format(addr, data.hex()))

    run(MockHandler(), logging.DEBUG)
