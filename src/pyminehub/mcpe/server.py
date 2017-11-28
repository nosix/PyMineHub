import asyncio
import multiprocessing as mp
import queue
import time
from collections import namedtuple
from logging import getLogger

from pyminehub.mcpe.network.codec import packet_codec
from pyminehub.mcpe.network.packet import PacketID, packet_factory
from pyminehub.network.address import to_address
from pyminehub.raknet.server import run as run_raknet

_logger = getLogger(__name__)


class MCPEServer:

    _INTERNAL_ADDRESSES = tuple(to_address(('0.0.0.0', 0)) for i in range(20))

    def __init__(self, send_queue: mp.Queue, receive_queue: mp.Queue):
        self._send_queue = send_queue
        self._receive_queue = receive_queue
        self._start_time = time.time()

    def _get_current_time(self):
        return int(time.time() - self._start_time)

    def sendto(self, packet: namedtuple, addr: tuple) -> None:
        self._send_queue.put_nowait((addr, packet_codec.encode(packet)))
        _logger.debug('< %s %s', addr, packet)

    async def run(self):
        while True:
            print('tick')
            self._receive_payload()
            await asyncio.sleep(1)

    def _receive_payload(self):
        try:
            addr, payload = self._receive_queue.get_nowait()
            _logger.debug('%s [%d] %s', addr, len(payload), payload.hex())
            packet = packet_codec.decode(payload)
            _logger.debug('> %s %s', addr, packet)
            getattr(self, 'process_' + PacketID(packet.id).name)(packet, addr)
        except queue.Empty:
            pass

    def process_connection_request(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.connection_request_accepted,
            to_address(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.time_since_start,
            self._get_current_time()
        )
        self.sendto(res_packet, addr)


def start_raknet(send_queue: mp.Queue, receive_queue: mp.Queue) -> mp.Process:
    raknet_process = mp.Process(
        target=run_raknet, args=(receive_queue, send_queue, logging.getLogger().getEffectiveLevel()))
    raknet_process.start()
    return raknet_process


def run():
    mp.set_start_method('spawn')
    send_queue, receive_queue = mp.Queue(), mp.Queue()
    raknet_process = start_raknet(send_queue, receive_queue)
    server = MCPEServer(send_queue, receive_queue)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.run())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        raknet_process.join()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
