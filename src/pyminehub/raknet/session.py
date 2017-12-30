import asyncio
from collections import defaultdict
from logging import getLogger
from typing import Callable, Dict, List, Set, Tuple

from pyminehub.network.codec import PACKET_HEADER_SIZE, RAKNET_WEIRD
from pyminehub.raknet.channel import Channel
from pyminehub.raknet.codec import raknet_packet_codec
from pyminehub.raknet.fragment import Fragment
from pyminehub.raknet.frame import Reliability, RakNetFrameType, RakNetFrame
from pyminehub.raknet.packet import RakNetPacketType, RakNetPacket, raknet_packet_factory
from pyminehub.raknet.sending import SendQueue
from pyminehub.value import LogString

_logger = getLogger(__name__)


def _create_send_packet(sequence_num: int, payload: bytes) -> RakNetPacket:
    return raknet_packet_factory.create(RakNetPacketType.FRAME_SET_4, sequence_num, payload)


_ALL_HEADER_SIZE = PACKET_HEADER_SIZE + RAKNET_WEIRD + len(raknet_packet_codec.encode(_create_send_packet(0, b'')))


class Session:

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            mtu_size: int,
            send_to_game_handler: Callable[[bytes], None],
            send_to_client: Callable[[RakNetPacket], None]
    ) -> None:
        self._send_to_game_handler = send_to_game_handler
        self._send_to_client = send_to_client
        self._expected_sequence_num = 0  # type: int  # next sequence number for receive packet
        self._ack_set = set()  # type: Set[int]  # waiting ACKs for sending
        self._nck_set = set()  # type: Set[int]  # waiting NCKs for sending
        self._resend_candidates = {}  # type: Dict[int, Tuple[int, ...]]  # sequence_num to reliable_message_num
        self._channels = defaultdict(Channel)  # type: Dict[int, Channel]
        self._fragment = Fragment()  # for split receive packet
        self._sequence_num = 0  # type: int  # next sequence number for send packet
        self._send_queue = SendQueue(mtu_size - _ALL_HEADER_SIZE, self._send_frame_set)
        self._sendable = asyncio.Event()
        self._sending_task = self._start_loop_to_send(loop)

    def _start_loop_to_send(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        async def loop_to_send():
            while True:
                await self._sendable.wait()
                self._send_waiting_packets()
                self._sendable.clear()
        return asyncio.ensure_future(loop_to_send(), loop=loop)

    def close(self):
        self._sending_task.cancel()
        self._send_waiting_packets()

    def frame_received(self, packet_sequence_num: int, frames: List[RakNetFrame]) -> None:
        # TODO make sure to need check reliable_message_num
        self._ack_set.add(packet_sequence_num)
        if packet_sequence_num == self._expected_sequence_num:
            self._expected_sequence_num += 1
        elif packet_sequence_num > self._expected_sequence_num:
            for nck_sequence_num in range(self._expected_sequence_num, packet_sequence_num):
                self._nck_set.add(nck_sequence_num)
            self._expected_sequence_num = packet_sequence_num + 1
        self._process_frames(frames)
        self._sendable.set()

    def _process_frames(self, frames: List[RakNetFrame]) -> None:
        for frame in frames:
            _logger.debug('> %s', LogString(frame))
            getattr(self, '_process_' + RakNetFrameType(frame.id).name.lower())(frame)

    def _process_unreliable(self, frame: RakNetFrame) -> None:
        self._send_to_game_handler(frame.payload)

    def _process_reliable(self, frame: RakNetFrame) -> None:
        self._send_to_game_handler(frame.payload)

    def _process_reliable_ordered(self, frame: RakNetFrame) -> None:
        channel = self._channels[frame.message_ordering_chanel]
        channel.append(frame)
        for payload in channel:
            self._send_to_game_handler(payload)

    def _process_reliable_ordered_has_split(self, frame: RakNetFrame) -> None:
        self._fragment.append(
            frame.split_packet_id,
            frame.split_packet_count,
            frame.split_packet_index,
            frame.payload)
        payload = self._fragment.pop(frame.split_packet_id)
        if payload is not None:
            # noinspection PyProtectedMember
            frame = frame._replace(payload=payload)
            self._process_reliable_ordered(frame)

    def nck_received(self, packet: RakNetPacket) -> None:
        self._nck_or_ack_received(packet, self._nck_action)

    def ack_received(self, packet: RakNetPacket) -> None:
        self._nck_or_ack_received(packet, self._ack_action)

    @staticmethod
    def _nck_or_ack_received(packet: RakNetPacket, action: Callable[[int], None]) -> None:
        min_sequence_num = packet.packet_sequence_number_min
        max_sequence_num = min_sequence_num if packet.range_max_equals_to_min else packet.packet_sequence_number_max
        for sequence_num in range(min_sequence_num, max_sequence_num + 1):
            action(sequence_num)

    def _nck_action(self, sequence_num: int) -> None:
        try:
            for reliable_sequence_num in self._resend_candidates[sequence_num]:
                self._send_queue.resend(reliable_sequence_num)
        except KeyError:
            pass

    def _ack_action(self, sequence_num: int) -> None:
        try:
            for reliable_sequence_num in self._resend_candidates[sequence_num]:
                self._send_queue.discard(reliable_sequence_num)
        except KeyError:
            pass

    def send_frame(self, payload: bytes, reliability: Reliability) -> None:
        self._send_queue.push(payload, reliability)
        self._sendable.set()

    def _send_waiting_packets(self) -> None:
        self._send_ack_or_nck(RakNetPacketType.ACK, self._ack_set)
        self._send_ack_or_nck(RakNetPacketType.NCK, self._nck_set)
        self._ack_set.clear()
        self._nck_set.clear()
        self._send_queue.send()

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

    def _send_frame_set(self, payload: bytes, reliable_sequence_num: Tuple[int, ...]) -> None:
        """Callback from SendQueue."""
        packet = _create_send_packet(self._sequence_num, payload)
        self._resend_candidates[packet.packet_sequence_num] = reliable_sequence_num
        self._sequence_num += 1
        self._send_to_client(packet)
