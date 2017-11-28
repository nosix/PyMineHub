import asyncio
from collections import namedtuple
from logging import getLogger, basicConfig
from multiprocessing import Queue

from pyminehub.raknet.codec import packet_codec, capsule_codec
from pyminehub.raknet.packet import PacketID, packet_factory
from pyminehub.raknet.session import Session

_logger = getLogger(__name__)


class _RakNetServerProtocol(asyncio.DatagramProtocol):

    IP_VERSION = 4

    def __init__(self, loop: asyncio.events.AbstractEventLoop, send_queue: Queue, receive_queue: Queue):
        self._loop = loop
        self._send_queue = send_queue
        self._receive_queue = receive_queue
        self._sessions = {}
        self.guid = 472877960873915066
        self.server_id = 'MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'

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

    def sendto(self, packet: namedtuple, addr: tuple) -> None:
        _logger.debug('< %s %s', addr, packet)
        self._transport.sendto(packet_codec.encode(packet), addr)

    def send_encapsulated_payload(self, payload: bytes, addr: tuple) -> None:
        self._send_queue.put_nowait((addr, payload))

    def send_ack_and_nck(self) -> None:
        for addr, session in self._sessions.items():
            def sendto(res_packet):
                self.sendto(res_packet, addr)
            session.send_ack_and_nck(sendto)

    def _process_unconnected_ping(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.unconnected_pong, packet.time_since_start, self.guid, True, self.server_id)
        self.sendto(res_packet, addr)

    def _process_open_connection_request1(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.open_connection_reply1, True, self.guid, False, packet.mtu_size)
        self.sendto(res_packet, addr)

    def _process_open_connection_request2(self, packet: namedtuple, addr: tuple) -> None:
        assert packet.server_ip_version == self.IP_VERSION
        host = bytes(int(v) for v in addr[0].split('.'))
        port = addr[1]
        res_packet = packet_factory.create(
            PacketID.open_connection_reply2, True, self.guid, self.IP_VERSION, host, port, packet.mtu_size, False)
        self.sendto(res_packet, addr)
        self._sessions[addr] = Session(lambda payload: self.send_encapsulated_payload(payload, addr))

    def _process_custom_packet_4(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        capsule = capsule_codec.decode(packet.payload)
        session.capsule_received(packet.packet_sequence_num, capsule)

    def _process_nck(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        session.remove_nck(packet)

    def _process_ack(self, packet: namedtuple, addr: tuple) -> None:
        session = self._sessions[addr]
        session.remove_ack(packet)


async def send(protocol: _RakNetServerProtocol):
    while True:
        await asyncio.sleep(0.1)
        protocol.send_ack_and_nck()


def run(send_queue, receive_queue, log_level=None):
    not log_level or basicConfig(level=log_level)
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        lambda: _RakNetServerProtocol(loop, send_queue, receive_queue), local_addr=('0.0.0.0', 19132))
    transport, protocol = loop.run_until_complete(listen)
    try:
        loop.run_until_complete(send(protocol))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()
        loop.close()


if __name__ == '__main__':
    import logging
    import multiprocessing as mp
    run(mp.Queue(), mp.Queue(), logging.DEBUG)
