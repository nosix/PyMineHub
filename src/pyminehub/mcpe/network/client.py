import asyncio
from logging import getLogger
from random import randrange

from pyminehub.mcpe.network.handler import MCPEDataHandler
from pyminehub.mcpe.network.packet import ConnectionPacket, connection_packet_factory, ConnectionPacketType
from pyminehub.mcpe.network.reliability import RELIABLE
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import AbstractClient

_logger = getLogger(__name__)


class MCPEClient(AbstractClient, MCPEDataHandler):

    def __init__(self) -> None:
        MCPEDataHandler.__init__(self)
        self._guid = randrange(1 << (8 * 8))  # long range
        self._connecting = asyncio.Event()
        self._request_time = None

    @property
    def guid(self) -> int:
        return self._guid

    def data_received(self, data: bytes, addr: Address) -> None:
        MCPEDataHandler.data_received(self, data, addr)

    async def start(self) -> None:
        self._request_time = self.get_current_time()
        send_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST, self.guid, self._request_time, False)
        self.send_connection_packet(send_packet, self.server_addr, RELIABLE)
        await self._connecting.wait()

    def update_status(self, addr: Address, is_connecting: bool) -> None:
        if is_connecting:
            self._connecting.set()

    def _process_connection_request_accepted(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.client_time_since_start != self._request_time:
            _logger.warning('The packet of connection request accepted has invalid time. (expected:%d, actual: %d)',
                            self._request_time, packet.client_time_since_start)
            return

        send_packet = connection_packet_factory.create(
            ConnectionPacketType.NEW_INCOMING_CONNECTION,
            to_packet_format(self.server_addr),
            self.INTERNAL_ADDRESSES,
            packet.server_time_since_start,
            self.get_current_time()
        )
        self.send_connection_packet(send_packet, addr, RELIABLE)

        self.send_ping(addr)
