from collections import defaultdict
from logging import getLogger
from typing import List, Set, Dict, Callable

from pyminehub.raknet.codec import raknet_packet_codec
from pyminehub.raknet.fragment import MessageFragment
from pyminehub.raknet.frame import Reliability, RakNetFrameType, RakNetFrame, raknet_frame_factory
from pyminehub.raknet.packet import RakNetPacketType, RakNetPacket, raknet_packet_factory
from pyminehub.raknet.queue import SendQueue

_logger = getLogger(__name__)


def _create_send_packet(sequence_num: int, payload: bytes) -> RakNetPacket:
    return raknet_packet_factory.create(RakNetPacketType.CUSTOM_PACKET_4, sequence_num, payload)


_PACKET_HEADER_SIZE = (
    20 +  # IP header size  # TODO why does need?
    8 +  # UDP header size  # TODO why does need?
    8 +  # RakNet weird ?   # TODO why does need?
    len(raknet_packet_codec.encode(_create_send_packet(0, b''))))


class Session:

    def __init__(self,
                 mtu_size: int,
                 send_to_game_handler: Callable[[bytes], None],
                 send_to_client: Callable[[RakNetPacket], None]
                 ) -> None:
        self._send_to_game_handler = send_to_game_handler
        self._send_to_client = send_to_client
        self._expected_sequence_num = 0  # type: int  # next sequence number for receive packet
        self._frame_cache = {}  # type: Dict[int, RakNetFrame]  # received frame cache
        self._ack_set = set()  # type: Set[int]  # waiting ACKs for sending
        self._nck_set = set()  # type: Set[int]  # waiting NCKs for sending
        self._fragment = MessageFragment()  # for split receive packet
        self._sequence_num = 0  # type: int  # next sequence number for send packet
        self._resend_cache = {}  # type: Dict[int, RakNetPacket]  # send packets waiting for ACK / NCK
        self._message_num = 0  # type: int  # for send reliable packet
        self._ordering_index = defaultdict(lambda: 0)  # type: Dict[int, int]  # for send reliable ordered packet
        self._send_queue = SendQueue(mtu_size - _PACKET_HEADER_SIZE, self._send_frames)

    def _get_packet_header_size(self) -> int:
        return len(raknet_packet_codec.encode(self._create_send_packet(0, b'')))

    @staticmethod
    def _create_send_packet(sequence_num: int, payload: bytes) -> RakNetPacket:
        return raknet_packet_factory.create(RakNetPacketType.CUSTOM_PACKET_4, sequence_num, payload)

    def frame_received(self, packet_sequence_num: int, frames: List[RakNetFrame]) -> None:
        if packet_sequence_num == self._expected_sequence_num:
            self._process_frames(packet_sequence_num, frames)
            self._expected_sequence_num += 1
            self._ack_set.add(packet_sequence_num)
            self._process_cache()
        elif packet_sequence_num > self._expected_sequence_num:
            self._frame_cache[packet_sequence_num] = frames
            for nck_sequence_num in range(self._expected_sequence_num, packet_sequence_num):
                self._nck_set.add(nck_sequence_num)
            self._ack_set.add(packet_sequence_num)
        else:
            _logger.warning('Packet that has old packet sequence number was received.')
            for frame in frames:
                _logger.warning('[%d] %s', packet_sequence_num, frame)

    def _process_cache(self) -> None:
        while self._expected_sequence_num in self._frame_cache:
            frames = self._frame_cache.pop(self._expected_sequence_num)
            self._process_frames(self._expected_sequence_num, frames)
            self._expected_sequence_num += 1

    def _process_frames(self, packet_sequence_num: int, frames: List[RakNetFrame]) -> None:
        for frame in frames:
            _logger.debug('> %d:%s', packet_sequence_num, frame)
            getattr(self, '_process_' + RakNetFrameType(frame.id).name.lower())(frame)

    def _process_unreliable(self, frame: RakNetFrame) -> None:
        self._send_to_game_handler(frame.payload)

    def _process_reliable(self, frame: RakNetFrame) -> None:
        self._send_to_game_handler(frame.payload)

    def _process_reliable_ordered(self, frame: RakNetFrame) -> None:
        self._send_to_game_handler(frame.payload)

    def _process_reliable_ordered_has_split(self, frame: RakNetFrame) -> None:
        self._fragment.append(
            frame.split_packet_id,
            frame.split_packet_count,
            frame.split_packet_index,
            frame.payload)
        payload = self._fragment.pop(frame.split_packet_id)
        if payload is not None:
            self._send_to_game_handler(payload)

    @staticmethod
    def _nck_or_ack_received(packet: RakNetPacket, action: Callable[[int], None]) -> None:
        min_sequence_num = packet.packet_sequence_number_min
        max_sequence_num = min_sequence_num if packet.range_max_equals_to_min else packet.packet_sequence_number_max
        for sequence_num in range(min_sequence_num, max_sequence_num + 1):
            action(sequence_num)

    def _nck_action(self, sequence_num: int) -> None:
        res_packet = self._resend_cache[sequence_num]
        self._send_to_client(res_packet)

    def _ack_action(self, sequence_num: int) -> None:
        del self._resend_cache[sequence_num]

    def nck_received(self, packet: RakNetPacket) -> None:
        self._nck_or_ack_received(packet, self._nck_action)

    def ack_received(self, packet: RakNetPacket) -> None:
        self._nck_or_ack_received(packet, self._ack_action)

    def _send_ack_or_nck(self, packet_id: RakNetPacketType, ack_set: Set[int]) -> None:
        sendto = self._send_to_client

        def send_ack_or_nck():
            diff_sequence_num = max_sequence_num - min_sequence_num + 1
            packet = raknet_packet_factory.create(
                packet_id,
                1,
                diff_sequence_num == 1,
                min_sequence_num,
                max_sequence_num if diff_sequence_num > 1 else None
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

    def send_waiting_pacckets(self) -> None:
        self._send_queue.send()
        self._send_ack_or_nck(RakNetPacketType.ACK, self._ack_set)
        self._send_ack_or_nck(RakNetPacketType.NCK, self._nck_set)
        self._ack_set.clear()
        self._nck_set.clear()

    def send_custom_packet(self, payload: bytes, reliability: Reliability) -> None:
        reliable, channel = reliability
        if channel is not None:
            self._send_reliable_ordered_frame(payload, channel)
        elif reliable:
            self._send_reliable_frame(payload)
        else:
            self._send_unreliable_frame(payload)

    def _send_reliable_ordered_frame(self, payload: bytes, channel: int) -> None:
        frame = raknet_frame_factory.create(
            RakNetFrameType.RELIABLE_ORDERED,
            len(payload) * 8,
            self._message_num,
            self._ordering_index[channel],
            channel,
            payload
        )
        self._send_queue.push(frame)
        self._message_num += 1
        self._ordering_index[channel] += 1

    def _send_reliable_frame(self, payload: bytes) -> None:
        frame = raknet_frame_factory.create(
            RakNetFrameType.RELIABLE,
            len(payload) * 8,
            self._message_num,
            payload
        )
        self._send_queue.push(frame)
        self._message_num += 1

    def _send_unreliable_frame(self, payload: bytes) -> None:
        frame = raknet_frame_factory.create(
            RakNetFrameType.UNRELIABLE,
            len(payload) * 8,
            payload
        )
        self._send_queue.push(frame)

    def _send_frames(self, payload: bytes) -> None:
        """Callback from SendQueue."""
        packet = _create_send_packet(self._sequence_num, payload)
        self._resend_cache[packet.packet_sequence_num] = packet
        self._sequence_num += 1
        self._send_to_client(packet)
