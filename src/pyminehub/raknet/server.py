import asyncio
from collections import namedtuple
from logging import getLogger

from pyminehub.raknet.codec import packet_codec, capsule_codec
from pyminehub.raknet.packet import PacketID, packet_factory

_logger = getLogger(__name__)


class _RakNetServerProtocol(asyncio.DatagramProtocol):

    IP_VERSION = 4

    def __init__(self, loop: asyncio.events.AbstractEventLoop):
        self.loop = loop
        self.guid = 472877960873915066
        self.server_id = 'MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        # noinspection PyAttributeOutsideInit
        self.transport = transport

    def process_unconnected_ping(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.unconnected_pong, packet.time_since_start, self.guid, True, self.server_id)
        self.transport.sendto(packet_codec.encode(res_packet), addr)

    def process_open_connection_request1(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.open_connection_reply1, True, self.guid, False, packet.mtu_size)
        self.transport.sendto(packet_codec.encode(res_packet), addr)

    def process_open_connection_request2(self, packet: namedtuple, addr: tuple) -> None:
        assert packet.server_ip_version == self.IP_VERSION
        host = bytes(int(v) for v in addr[0].split('.'))
        port = addr[1]
        res_packet = packet_factory.create(
            PacketID.open_connection_reply2, True, self.guid, self.IP_VERSION, host, port, packet.mtu_size, False)
        self.transport.sendto(packet_codec.encode(res_packet), addr)

    def process_custom_packet_4(self, packet: namedtuple, addr: tuple) -> None:
        capsule = capsule_codec.decode(packet.payload)
        _logger.debug('%s', capsule)

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = packet_codec.decode(data)
        _logger.debug('%s', packet)
        getattr(self, 'process_' + PacketID(packet.id).name)(packet, addr)

    def connection_lost(self, exc: Exception):
        _logger.exception('RakNet connection lost', exc_info=exc)
        self.loop.stop()


async def hello():
    while True:
        print('Hello world')
        await asyncio.sleep(1)


def run():
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        lambda: _RakNetServerProtocol(loop), local_addr=('0.0.0.0', 19132))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_until_complete(hello())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()
        loop.close()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
