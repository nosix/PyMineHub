import time
from logging import getLogger
from typing import Dict

from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacket, GamePacket, ConnectionPacketType, connection_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.network.reliability import UNRELIABLE
from pyminehub.network.address import Address, to_packet_format, get_unspecified_address
from pyminehub.raknet import GameDataHandler, Reliability
from pyminehub.value import LogString

_logger = getLogger(__name__)


class MCPEDataHandler(GameDataHandler):

    INTERNAL_ADDRESSES = tuple(to_packet_format((get_unspecified_address(), 0)) for _ in range(20))

    def __init__(self) -> None:
        self._start_time = time.time()
        self._ping_time = {}  # type: Dict[Address, int]
        self._queue = GamePacketQueue(self.send_connection_packet)

    # GameDataHandler interface methods

    def data_received(self, data: bytes, addr: Address) -> None:
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s', LogString(packet))
        getattr(self, '_process_' + packet.type.name.lower())(packet, addr)

    async def update(self) -> None:
        raise NotImplementedError()

    def terminate(self) -> None:
        raise NotImplementedError()

    # local methods

    def update_status(self, addr: Address, is_connecting: bool) -> None:
        raise NotImplementedError()

    def send_connection_packet(self, packet: ConnectionPacket, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: frame reliability
        """
        _logger.debug('< %s', LogString(packet))
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    def send_game_packet(self, packet: GamePacket, addr: Address, immediately=True) -> None:
        if immediately:
            self._queue.send_immediately(packet, addr)
        else:
            self._queue.append(packet, addr)

    def send_waiting_game_packet(self) -> None:
        self._queue.send()

    def send_ping(self, addr: Address) -> None:
        self._ping_time[addr] = self.get_current_time()
        packet = connection_packet_factory.create(ConnectionPacketType.CONNECTED_PING, self._ping_time[addr])
        self.send_connection_packet(packet, addr, UNRELIABLE)

    def get_current_time(self) -> int:
        """Get millisecond time since starting handler."""
        return int(1000 * (time.time() - self._start_time))

    def _process_batch(self, packet: ConnectionPacket, addr: Address) -> None:
        last_index = len(packet.payloads) - 1
        for i, data in enumerate(packet.payloads):
            try:
                packet = game_packet_codec.decode(data)
                _logger.debug('> %s', LogString(packet))
                getattr(self, '_process_' + packet.type.name.lower())(packet, addr, i == last_index)
            except AttributeError as exc:
                _logger.exception('%s', exc)
            except KeyError as exc:
                _logger.exception('%s is not supported in batch processing.', exc)

    def _process_connected_ping(self, packet: ConnectionPacket, addr: Address) -> None:
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PONG,
            packet.ping_time_since_start,
            self.get_current_time())
        self.send_connection_packet(res_packet, addr, UNRELIABLE)

    def _process_connected_pong(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.ping_time_since_start != self._ping_time[addr]:
            _logger.warning(
                'Pong time is invalid. (expected: %d, actual: %d)',
                self._ping_time[addr], packet.ping_time_since_start)
        self.update_status(addr, True)
        # TODO send ping
