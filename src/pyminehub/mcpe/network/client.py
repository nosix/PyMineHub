import asyncio
import uuid
from logging import getLogger
from random import randrange

from pyminehub.mcpe.const import CommandOriginDataType
from pyminehub.mcpe.network.handler import MCPEDataHandler
from pyminehub.mcpe.network.packet import *
from pyminehub.mcpe.network.reliability import RELIABLE, DEFAULT_CHANEL
from pyminehub.mcpe.value import CommandOriginData
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import AbstractClient, GameDataHandler

_logger = getLogger(__name__)


class MCPEClientHandler(MCPEDataHandler):

    def __init__(self) -> None:
        super().__init__()
        self._guid = randrange(1 << (8 * 8))  # long range
        self._uuid = uuid.uuid4()
        self._connecting = asyncio.Event()
        self._queue = asyncio.Queue()
        self._request_time = None

    # GameDataHandler interface methods

    @property
    def guid(self) -> int:
        return self._guid

    async def update(self) -> None:
        await asyncio.Event().wait()

    def terminate(self) -> None:
        pass

    # MCPEDataHandler method

    def update_status(self, addr: Address, is_connecting: bool) -> None:
        if is_connecting:
            self._connecting.set()

    # local methods

    async def start(self, server_addr: Address) -> None:
        self._request_time = self.get_current_time()
        send_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST, self.guid, self._request_time, False)
        self.send_connection_packet(send_packet, server_addr, RELIABLE)
        await self._connecting.wait()

    def send_command_request(self, server_addr: Address, command: str) -> None:
        send_packet = game_packet_factory.create(
            GamePacketType.COMMAND_REQUEST,
            EXTRA_DATA,
            command,
            CommandOriginData(CommandOriginDataType.DEV_CONSOLE, self._uuid, '', 0),
            True
        )
        self.send_game_packet(send_packet, server_addr, DEFAULT_CHANEL)

    async def wait_response(self) -> GamePacket:
        return await self._queue.get()

    def _process_connection_request_accepted(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.client_time_since_start != self._request_time:
            _logger.warning('The packet of connection request accepted has invalid time. (expected:%d, actual: %d)',
                            self._request_time, packet.client_time_since_start)
            return

        send_packet = connection_packet_factory.create(
            ConnectionPacketType.NEW_INCOMING_CONNECTION,
            to_packet_format(addr),
            self.INTERNAL_ADDRESSES,
            packet.server_time_since_start,
            self.get_current_time()
        )
        self.send_connection_packet(send_packet, addr, RELIABLE)

        self.send_ping(addr)

    # noinspection PyUnusedLocal
    def _process_text(self, packet: GamePacket, addr: Address) -> None:
        # TODO check text_type and needs_translation
        parameters = tuple(str(p) for p in packet.parameters)
        if len(parameters) > 0:
            _logger.info('%s: %s (%s)', packet.type.name, packet.message, ', '.join(parameters))
        else:
            _logger.info('%s: %s', packet.type.name, packet.message)
        self._queue.put_nowait(packet)


class MCPEClient(AbstractClient):

    def __init__(self) -> None:
        self._handler = MCPEClientHandler()

    # AbstractClient methods

    @property
    def handler(self) -> GameDataHandler:
        return self._handler

    async def start(self) -> None:
        await self._handler.start(self.server_addr)

    # local methods

    def wait_response(self) -> GamePacket:
        return self.loop.run_until_complete(self._handler.wait_response())

    def execute_command(self, command: str) -> None:
        self._handler.send_command_request(self.server_addr, command)
