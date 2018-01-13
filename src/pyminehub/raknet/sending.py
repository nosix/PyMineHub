import math
import time
from collections import defaultdict
from logging import getLogger
from queue import Empty
from typing import Callable, Dict, Generator, Tuple

from pyminehub.config import ConfigKey, get_value
from pyminehub.queue import UpdatablePriorityQueue
from pyminehub.raknet.codec import raknet_frame_codec
from pyminehub.raknet.frame import Reliability, RakNetFrameType, RakNetFrame, raknet_frame_factory
from pyminehub.value import LogString

_logger = getLogger(__name__)


def _get_header_size() -> Dict[RakNetFrameType, int]:
    frame_args = {
        RakNetFrameType.UNRELIABLE: (0, b''),
        RakNetFrameType.RELIABLE: (0, 0, b''),
        RakNetFrameType.RELIABLE_ORDERED: (0, 0, 0, 0, b''),
        RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: (0, 0, 0, 0, 0, 0, 0, b'')
    }
    return dict(
        (
            frame_id,
            len(raknet_frame_codec.encode(raknet_frame_factory.create(frame_id, *args)))
        ) for frame_id, args in frame_args.items())


_HEADER_SIZE_DICT = _get_header_size()


def _to_frame_type(reliability: Reliability) -> RakNetFrameType:
    if reliability.channel is not None:
        return RakNetFrameType.RELIABLE_ORDERED
    if reliability.reliable:
        return RakNetFrameType.RELIABLE
    else:
        return RakNetFrameType.UNRELIABLE


def _get_encoded_size(payload: bytes, frame_type: RakNetFrameType) -> int:
    return _HEADER_SIZE_DICT[frame_type] + len(payload)


def _get_bit_length(payload: bytes) -> int:
    return len(payload) * 8


def _is_reliable(frame: RakNetFrame) -> bool:
    return frame.type != RakNetFrameType.UNRELIABLE


class SendQueue:

    def __init__(self, max_payload_size: int, send_frames: Callable[[bytes, Tuple[int, ...]], None]) -> None:
        self._max_payload_size = max_payload_size
        self._max_fragmented_payload_size = \
            max_payload_size - _HEADER_SIZE_DICT[RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT]
        self._send_frames = send_frames
        self._queue = UpdatablePriorityQueue(
            lambda frame: frame.reliable_message_num if _is_reliable(frame) else None)
        self._message_num = 0  # type: int  # for send reliable packet
        self._ordering_index = defaultdict(lambda: 0)  # type: Dict[int, int]  # for send reliable ordered packet
        self._split_packet_id = 0  # next split_packet_id

    @staticmethod
    def _get_current_time() -> float:
        return time.time()

    @staticmethod
    def _get_resend_time_in_future() -> int:
        return time.time() + get_value(ConfigKey.RESEND_TIME)

    def push(self, payload: bytes, reliability: Reliability, send_time_in_future=0) -> None:
        for frame in self._create_frame(payload, reliability):
            _logger.debug('< %s', LogString(frame))
            self._queue.put(self._get_current_time() + send_time_in_future, frame)

    def discard(self, reliable_message_num: int) -> None:
        self._queue.pop(reliable_message_num)

    def resend(self, reliable_message_num: int) -> None:
        frame = self._queue.pop(reliable_message_num)
        self._queue.put(self._get_current_time(), frame)

    def send(self) -> None:
        buffer = bytearray()
        reliable_message_num_in_buffer = []
        while True:
            try:
                send_time, frame = self._queue.get()
            except Empty:
                break

            if send_time > self._get_current_time():
                self._queue.put(send_time, frame)
                break

            if _is_reliable(frame):
                self._queue.put(self._get_resend_time_in_future(), frame)

            frame_size = _get_encoded_size(frame.payload, frame.type)
            assert frame_size <= self._max_payload_size
            if len(buffer) + frame_size > self._max_payload_size:
                self._send_frames(bytes(buffer), tuple(reliable_message_num_in_buffer))
                del buffer[:]  # faster than buffer = bytearray()
                reliable_message_num_in_buffer = []

            buffer.extend(raknet_frame_codec.encode(frame))
            if _is_reliable(frame):
                reliable_message_num_in_buffer.append(frame.reliable_message_num)

        if len(buffer) > 0:
            self._send_frames(bytes(buffer), tuple(reliable_message_num_in_buffer))

    def _next_reliable_message_num(self) -> int:
        reliable_message_num = self._message_num
        self._message_num += 1
        return reliable_message_num

    def _next_ordering_index(self, channel: int) -> int:
        ordering_index = self._ordering_index[channel]
        self._ordering_index[channel] += 1
        return ordering_index

    def _next_split_packet_id(self) -> int:
        split_packet_id = self._split_packet_id
        self._split_packet_id += 1
        return split_packet_id

    def _create_frame(self, payload: bytes, reliability: Reliability) -> Generator[RakNetFrame, None, None]:
        frame_type = _to_frame_type(reliability)
        frame_size = _get_encoded_size(payload, frame_type)
        if frame_size > self._max_payload_size:
            assert frame_type == RakNetFrameType.RELIABLE_ORDERED
            frame_type = RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT

        if frame_type == RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT:
            ordering_index = self._next_ordering_index(reliability.channel)
            split_packet_count = math.ceil(len(payload) / self._max_fragmented_payload_size)  # type: int
            split_packet_id = self._next_split_packet_id()
            for split_packet_index in range(split_packet_count):
                payload_fragment = payload[:self._max_fragmented_payload_size]
                payload = payload[self._max_fragmented_payload_size:]
                yield raknet_frame_factory.create(
                    frame_type,
                    _get_bit_length(payload_fragment),
                    self._next_reliable_message_num(),
                    ordering_index,
                    reliability.channel,
                    split_packet_count,
                    split_packet_id,
                    split_packet_index,
                    payload_fragment
                )
        elif frame_type == RakNetFrameType.RELIABLE_ORDERED:
            yield raknet_frame_factory.create(
                RakNetFrameType.RELIABLE_ORDERED,
                _get_bit_length(payload),
                self._next_reliable_message_num(),
                self._next_ordering_index(reliability.channel),
                reliability.channel,
                payload
            )
        elif frame_type == RakNetFrameType.RELIABLE:
            yield raknet_frame_factory.create(
                frame_type,
                _get_bit_length(payload),
                self._next_reliable_message_num(),
                payload
            )
        elif frame_type == RakNetFrameType.UNRELIABLE:
            yield raknet_frame_factory.create(
                frame_type,
                _get_bit_length(payload),
                payload
            )
        else:
            assert False, 'Reliability {} is not supported.'.format(reliability)
