from collections import defaultdict
from typing import Callable, Dict, List, Tuple

from pyminehub.mcpe.network.codec import game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType, ConnectionPacket, connection_packet_factory
from pyminehub.mcpe.network.packet import GamePacketType, GamePacket
from pyminehub.mcpe.network.reliability import RELIABILITY_DICT
from pyminehub.network.address import Address
from pyminehub.raknet import Reliability


class _BatchQueue:

    def __init__(self) -> None:
        self._packets = []  # type: List[Tuple[Reliability, GamePacket]]

    def append(self, packet: GamePacket) -> None:
        """Append batch request.

        :param packet: game packet
        """
        self._packets.append((RELIABILITY_DICT[GamePacketType(packet.id)], packet))

    def send(self, sendto: Callable[[ConnectionPacket, Reliability], None]) -> None:
        payloads = []
        last_reliability = None
        for reliability, packet in self._packets:
            if last_reliability is not None and last_reliability != reliability:
                batch_packet = connection_packet_factory.create(ConnectionPacketType.BATCH, payloads)
                sendto(batch_packet, last_reliability)
                payloads = []
            payloads.append(game_packet_codec.encode(packet))
            last_reliability = reliability
        batch_packet = connection_packet_factory.create(ConnectionPacketType.BATCH, payloads)
        sendto(batch_packet, last_reliability)
        self._packets.clear()


class GamePacketQueue:

    def __init__(self, send_connection_packet: Callable[[ConnectionPacket, Address, Reliability], None]) -> None:
        self._send_connection_packet = send_connection_packet
        self._batch_queue = defaultdict(_BatchQueue)  # type: Dict[Address, _BatchQueue]

    def append(self, packet: GamePacket, addr: Address) -> None:
        """Register batch request.

        :param packet: game packet
        :param addr: destination
        """
        self._batch_queue[addr].append(packet)

    def send(self) -> None:
        for addr, queue in self._batch_queue.items():
            queue.send(lambda _packet, _reliability: self._send_connection_packet(_packet, addr, _reliability))

    def send_immediately(self, packet: GamePacket, addr: Address) -> None:
        self.append(packet, addr)
        self.send()
