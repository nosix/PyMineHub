import asyncio
from logging import getLogger

from pyminehub.binutil.composite import CompositeCodecContext
from pyminehub.network.address import Address
from pyminehub.raknet.codec import raknet_packet_codec, raknet_frame_codec
from pyminehub.raknet.handler import Reliability, RakNetProtocol, GameDataHandler, SessionNotFound
from pyminehub.raknet.packet import RakNetPacket
from pyminehub.raknet.session import Session
from pyminehub.value import LogString

_logger = getLogger(__name__)


class AbstractRakNetProtocol(asyncio.DatagramProtocol, RakNetProtocol):

    def __init__(self, loop: asyncio.events.AbstractEventLoop, handler: GameDataHandler, stop_loop: bool=True) -> None:
        """
        :param loop: it perform handler and session update
        :param handler: it handle GamePacket
        :param stop_loop: True if you want to stop loop when connection lost
        """
        handler.register_protocol(self)
        self._loop = loop
        self._handler = handler
        self._stop_loop = stop_loop
        self._transport = None
        self._update_task = self._start_loop_to_update(loop)

    def _start_loop_to_update(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        async def loop_to_update():
            while True:
                await self._next_moment()
        return asyncio.ensure_future(loop_to_update(), loop=loop)

    def terminate(self) -> None:
        self._update_task.cancel()

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        self._transport = transport

    def connection_lost(self, exc: Exception) -> None:
        _logger.exception('RakNet connection lost', exc_info=exc)
        self._transport = None
        if self._stop_loop:
            self._loop.stop()

    def datagram_received(self, data: bytes, addr: Address) -> None:
        _logger.debug('%s > %s', addr, data.hex())
        packet = raknet_packet_codec.decode(data)
        _logger.debug('> %s', LogString(packet))
        try:
            getattr(self, '_process_' + packet.type.name.lower())(packet, addr)
        except SessionNotFound:
            _logger.info('%s session is not found.', addr)
            self.remove_session(addr)

    def game_data_received(self, data: bytes, addr: Address, reliability: Reliability) -> None:
        session = self.get_session(addr)
        session.send_frame(data, reliability)

    def send_to_remote(self, packet: RakNetPacket, addr: Address) -> None:
        _logger.debug('< %s', LogString(packet))
        data = raknet_packet_codec.encode(packet)
        _logger.debug('%s < %s', addr, data.hex())
        self._transport.sendto(data, addr)

    async def _next_moment(self) -> None:
        try:
            await self._handler.update()
        except SessionNotFound as exc:
            if exc.addr is not None:
                _logger.info('%s session is not found.', exc.addr)
                self.remove_session(exc.addr)

    def create_session(self, mtu_size: int, addr: Address) -> Session:
        return Session(
            self._loop, mtu_size,
            lambda _data: self._handler.data_received(_data, addr),
            lambda _packet: self.send_to_remote(_packet, addr))

    def remove_session(self, addr: Address) -> None:
        raise NotImplementedError()

    def get_session(self, addr: Address) -> Session:
        raise NotImplementedError()

    def _process_frame_set(self, packet: RakNetPacket, addr: Address) -> None:
        session = self.get_session(addr)
        context = CompositeCodecContext()
        frames = []
        length = 0
        while length < len(packet.payload):
            payload = packet.payload[length:]
            frames.append(raknet_frame_codec.decode(payload, context))
            length += context.length
            context.clear()
        session.frame_received(packet.packet_sequence_num, frames)

    def _process_frame_set_4(self, packet: RakNetPacket, addr: Address) -> None:
        self._process_frame_set(packet, addr)

    def _process_frame_set_8(self, packet: RakNetPacket, addr: Address) -> None:
        self._process_frame_set(packet, addr)

    def _process_frame_set_c(self, packet: RakNetPacket, addr: Address) -> None:
        self._process_frame_set(packet, addr)

    def _process_nck(self, packet: RakNetPacket, addr: Address) -> None:
        session = self.get_session(addr)
        session.nck_received(packet)

    def _process_ack(self, packet: RakNetPacket, addr: Address) -> None:
        session = self.get_session(addr)
        session.ack_received(packet)
