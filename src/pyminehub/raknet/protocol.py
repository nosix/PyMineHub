import asyncio
from logging import getLogger

from pyminehub.network.address import Address
from pyminehub.network.handler import GameDataHandler, Protocol, SessionNotFound, Reliability
from pyminehub.raknet.codec import raknet_packet_codec, split_frame_set
from pyminehub.raknet.packet import RakNetPacket
from pyminehub.raknet.session import Session
from pyminehub.value import LogString

__all__ = [
    'AbstractRakNetProtocol'
]


_logger = getLogger(__name__)


class AbstractRakNetProtocol(asyncio.DatagramProtocol, Protocol):

    def __init__(self, handler: GameDataHandler) -> None:
        """
        :param handler: it handle GamePacket
        """
        handler.register_protocol(self)
        self.__handler = handler
        self.__transport = None

    @property
    def guid(self) -> int:
        return self.__handler.guid

    def terminate(self) -> None:
        pass

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        self.__transport = transport

    def connection_lost(self, exc: Exception) -> None:
        _logger.info('RakNet connection lost. (exception=%s)', exc)
        self.__transport = None

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
        self.__transport.sendto(data, addr)

    def create_session(self, mtu_size: int, addr: Address) -> Session:
        return Session(
            mtu_size,
            lambda _data: self.__handler.data_received(_data, addr),
            lambda _packet: self.send_to_remote(_packet, addr))

    def remove_session(self, addr: Address) -> bool:
        raise NotImplementedError()

    def get_session(self, addr: Address) -> Session:
        raise NotImplementedError()

    def _process_frame_set(self, packet: RakNetPacket, addr: Address) -> None:
        session = self.get_session(addr)
        frames = split_frame_set(packet.payload)
        session.frame_received(packet.packet_sequence_num, frames)

    def _process_frame_set_0(self, packet: RakNetPacket, addr: Address) -> None:
        self._process_frame_set(packet, addr)

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
