from collections import namedtuple
from logging import getLogger
from typing import Callable

from pyminehub.raknet.codec import capsule_codec
from pyminehub.raknet.encapsulation import CapsuleID, capsule_factory
from pyminehub.raknet.packet import PacketID, packet_factory

_logger = getLogger(__name__)


class Session:

    def __init__(self, send_to_game_server: Callable[[bytes], None], send_to_client: Callable[[namedtuple], None]):
        self._send_to_game_server = send_to_game_server
        self._send_to_client = send_to_client
        self._expected_sequence_num = 0
        self._ack_set = set()
        self._nck_set = set()
        self._capsule_cache = {}
        self._reliable_message_num = 0
        self._message_ordering_index = 0
        self._sequence_num = 0
        self._resend_queue = {}

    def capsule_received(self, packet_sequence_num: int, capsule: namedtuple) -> None:
        _logger.debug('> %d:%s', packet_sequence_num, capsule)
        getattr(self, '_process_' + CapsuleID(capsule.id).name)(packet_sequence_num, capsule)

    def _process_reliable(self, packet_sequence_num: int, capsule: namedtuple) -> None:
        assert capsule.payload_length / 8 == len(capsule.payload)
        if packet_sequence_num == self._expected_sequence_num:
            self._send_to_game_server(capsule.payload)
            self._expected_sequence_num += 1
            self._ack_set.add(packet_sequence_num)
            self._process_cache()
        elif packet_sequence_num > self._expected_sequence_num:
            self._capsule_cache[packet_sequence_num] = capsule
            for nck_sequence_num in range(self._expected_sequence_num, packet_sequence_num):
                self._nck_set.add(nck_sequence_num)
            self._ack_set.add(packet_sequence_num)
        else:
            _logger.warning('Packet that has old packet sequence number was received.')
            _logger.warning('[%d] %s', packet_sequence_num, capsule)

    def _process_cache(self) -> None:
        while self._expected_sequence_num in self._capsule_cache:
            capsule = self._capsule_cache.pop(self._expected_sequence_num)
            self._send_to_game_server(capsule.payload)
            self._expected_sequence_num += 1

    @staticmethod
    def _nck_or_ack_received(packet: namedtuple, action: Callable[[int], None]) -> None:
        min_sequence_num = packet.packet_sequence_number_min
        max_sequence_num = min_sequence_num if packet.range_max_equals_to_min else packet.packet_sequence_number_max
        for sequence_num in range(min_sequence_num, max_sequence_num + 1):
            action(sequence_num)

    def _nck_action(self, sequence_num):
        res_packet = self._resend_queue[sequence_num]
        self._send_to_client(res_packet)

    def _ack_action(self, sequence_num):
        del self._resend_queue[sequence_num]

    def nck_received(self, packet: namedtuple) -> None:
        self._nck_or_ack_received(packet, self._nck_action)

    def ack_received(self, packet: namedtuple) -> None:
        self._nck_or_ack_received(packet, self._ack_action)

    @staticmethod
    def _send_ack_or_nck(packet_id, ack_set, sendto: Callable[[namedtuple], None]):
        def send_ack_or_nck():
            record_count = max_sequence_num - min_sequence_num + 1
            packet = packet_factory.create(
                packet_id,
                record_count,
                record_count == 1,
                min_sequence_num,
                max_sequence_num if record_count > 1 else None
            )
            sendto(packet)

        min_sequence_num = None
        max_sequence_num = None
        for sequence_num in sorted(ack_set):
            if min_sequence_num is None:
                min_sequence_num = sequence_num
                max_sequence_num = sequence_num
            elif max_sequence_num == sequence_num - 1:
                max_sequence_num = sequence_num
            else:
                send_ack_or_nck()
                min_sequence_num = None
                max_sequence_num = None
        if min_sequence_num is not None:
            send_ack_or_nck()

    def send_ack_and_nck(self, sendto: Callable[[namedtuple], None]) -> None:
        self._send_ack_or_nck(PacketID.ack, self._ack_set, sendto)
        self._send_ack_or_nck(PacketID.nck, self._nck_set, sendto)
        self._ack_set.clear()
        self._nck_set.clear()

    def send_custom_packet(self, payload: bytes) -> None:
        capsule = capsule_factory.create(
            CapsuleID.reliable_ordered,
            len(payload) * 8,
            self._reliable_message_num,
            self._message_ordering_index,
            0,
            payload
        )
        packet = packet_factory.create(PacketID.custom_packet_4, self._sequence_num, capsule_codec.encode(capsule))
        _logger.debug('< %d:%s', packet.packet_sequence_num, capsule)
        self._send_to_client(packet)
        self._resend_queue[packet.packet_sequence_num] = packet
        self._reliable_message_num += 1
        self._message_ordering_index += 1
        self._sequence_num += 1