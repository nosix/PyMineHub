import time
from collections import namedtuple
from logging import getLogger

from pyminehub.mcpe.network.codec import packet_codec
from pyminehub.mcpe.network.packet import PacketID, packet_factory
from pyminehub.network.address import to_address
from pyminehub.raknet.server import GameDataHandler

_logger = getLogger(__name__)


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = tuple(to_address(('0.0.0.0', 0)) for i in range(20))

    def __init__(self):
        self._start_time = time.time()

    def _get_current_time(self):
        return int(time.time() - self._start_time)

    def data_received(self, data: bytes, addr: tuple) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, 'process_' + PacketID(packet.id).name)(packet, addr)

    def send_to_client(self, packet: namedtuple, addr: tuple) -> None:
        _logger.debug('< %s %s', addr, packet)
        self.sendto(packet_codec.encode(packet), addr)

    def process_connection_request(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = packet_factory.create(
            PacketID.connection_request_accepted,
            to_address(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.time_since_start,
            self._get_current_time()
        )
        self.send_to_client(res_packet, addr)
