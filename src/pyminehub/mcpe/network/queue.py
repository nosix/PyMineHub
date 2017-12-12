from collections import namedtuple, defaultdict
from typing import Callable, Dict, List, Tuple

from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import GamePacketID, ConnectionPacketID, connection_packet_factory
from pyminehub.network.address import Address
from pyminehub.raknet import Reliability

_RELIABILITY_CHANEL_DEFAULT = Reliability(True, 0)


class _BatchQueue:

    _RELIABILITY = {
        GamePacketID.PLAY_STATUS: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.RESOURCE_PACKS_INFO: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.RESOURCE_PACK_STACK: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.START_GAME: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.SET_TIME: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.UPDATE_ATTRIBUTES: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.AVAILABLE_COMMANDS: _RELIABILITY_CHANEL_DEFAULT,
        GamePacketID.ADVENTURE_SETTINGS: _RELIABILITY_CHANEL_DEFAULT
    }

    def __init__(self):
        self._packets = []  # type: List[Tuple[Reliability, namedtuple]]

    def append(self, packet: namedtuple) -> None:
        """Append batch request.

        :param packet: game packet
        """
        self._packets.append((self._RELIABILITY[GamePacketID(packet.id)], packet))

    def send(self, sendto: Callable[[namedtuple, Reliability], None]) -> None:
        payloads = []
        last_reliability = None
        for reliability, packet in self._packets:
            if last_reliability is not None and last_reliability != reliability:
                batch_packet = connection_packet_factory.create(ConnectionPacketID.BATCH, payloads)
                sendto(batch_packet, last_reliability)
                payloads = []
            payloads.append(game_packet_codec.encode(packet))
            last_reliability = reliability
        batch_packet = connection_packet_factory.create(ConnectionPacketID.BATCH, payloads)
        sendto(batch_packet, last_reliability)
        self._packets.clear()


class GamePacketQueue:

    def __init__(self, send_connection_packet: Callable[[namedtuple, Address, Reliability], None]):
        self._send_connection_packet = send_connection_packet
        self._batch_queue = defaultdict(_BatchQueue)  # type: Dict[Address, _BatchQueue]

    def append(self, packet: namedtuple, addr: Address) -> None:
        """Register batch request.

        :param packet: game packet
        :param addr: destination
        """
        self._batch_queue[addr].append(packet)

    def send(self) -> None:
        for addr, queue in self._batch_queue.items():
            queue.send(lambda _packet, _reliability: self._send_connection_packet(_packet, addr, _reliability))

    def send_immediately(self, packet: namedtuple, addr: Address) -> None:
        self.append(packet, addr)
        self.send()
