import asyncio
import multiprocessing as mp
import queue
from collections import namedtuple
from logging import getLogger

from pyminehub.mcpe.network.codec import PacketID, packet_codec
from pyminehub.raknet.server import run as run_raknet

_logger = getLogger(__name__)


class MCPEServer:

    async def run(self, send_queue: mp.Queue, receive_queue: mp.Queue):
        while True:
            print('tick')
            try:
                addr, data = receive_queue.get_nowait()
                _logger.debug('%s [%d] %s', addr, len(data), data.hex())
                packet = packet_codec.decode(data)
                _logger.debug('%s', packet)
                getattr(self, 'process_' + PacketID(packet.id).name)(packet, addr)
            except queue.Empty:
                pass
            await asyncio.sleep(1)

    def process_connection_request(self, packet: namedtuple, addr: tuple) -> None:
        pass


def start_raknet(send_queue: mp.Queue, receive_queue: mp.Queue) -> mp.Process:
    raknet_process = mp.Process(
        target=run_raknet, args=(receive_queue, send_queue, logging.getLogger().getEffectiveLevel()))
    raknet_process.start()
    return raknet_process


def run():
    mp.set_start_method('spawn')
    send_queue, receive_queue = mp.Queue(), mp.Queue()
    raknet_process = start_raknet(send_queue, receive_queue)
    server = MCPEServer()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server.run(send_queue, receive_queue))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        raknet_process.join()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
