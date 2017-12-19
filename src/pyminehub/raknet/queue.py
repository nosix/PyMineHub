import math
import time
from queue import PriorityQueue
from typing import Callable, Set, Dict, Generator

from pyminehub.config import ConfigKey, get_value
from pyminehub.raknet.codec import raknet_frame_codec
from pyminehub.raknet.frame import RakNetFrameType, RakNetFrame, raknet_frame_factory


def _get_header_size() -> Dict[int, int]:
    frame_args = {
        RakNetFrameType.UNRELIABLE: (0, b''),
        RakNetFrameType.RELIABLE: (0, 0, b''),
        RakNetFrameType.RELIABLE_ORDERED: (0, 0, 0, 0, b''),
        RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT: (0, 0, 0, 0, 0, 0, 0, b'')
    }
    return dict(
        (
            frame_id.value,
            len(raknet_frame_codec.encode(raknet_frame_factory.create(frame_id, *args)))
        ) for frame_id, args in frame_args.items())


_HEADER_SIZE_DICT = _get_header_size()


def _get_encoded_size(frame: RakNetFrame) -> int:
    return _HEADER_SIZE_DICT[frame.id] + frame.payload_length // 8


class SendQueue:

    def __init__(self, max_payload_size: int, send_frames: Callable[[bytes], None]) -> None:
        self._max_payload_size = max_payload_size
        self._max_fragmented_payload_size = \
            max_payload_size - _HEADER_SIZE_DICT[RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT.value]
        self._send_frames = send_frames
        self._queue = PriorityQueue()
        self._messages_to_be_discarded = set()  # type: Set[int]  # set of reliable_message_num
        self._next_split_packet_id = 0

    @staticmethod
    def _get_current_time() -> int:
        return time.time()

    @staticmethod
    def _get_resend_time_in_future() -> int:
        return time.time() + get_value(ConfigKey.RESEND_TIME)

    def push(self, frame: RakNetFrame, send_time_in_future=0) -> None:
        self._queue.put_nowait((self._get_current_time() + send_time_in_future, frame))

    def discard(self, reliable_message_num: int) -> None:
        self._messages_to_be_discarded.add(reliable_message_num)

    def send(self) -> None:
        buffer = bytearray()
        while not self._queue.empty():
            send_time, frame = self._queue.get_nowait()
            if send_time > self._get_current_time():
                self._queue.put_nowait((send_time, frame))
                break
            if hasattr(frame, 'reliable_message_num'):
                if frame.reliable_message_num in self._messages_to_be_discarded:
                    continue
                else:
                    self._queue.put_nowait((self._get_resend_time_in_future(), frame))

            frame_size = _get_encoded_size(frame)
            if len(buffer) > 0 and len(buffer) + frame_size > self._max_payload_size:
                self._send_frames(bytes(buffer))
                buffer = bytearray()
            if frame_size > self._max_payload_size:
                assert len(buffer) == 0
                for fragment in self._split_frame(frame):
                    self._send_frames(raknet_frame_codec.encode(fragment))
            else:
                buffer.extend(raknet_frame_codec.encode(frame))
        if len(buffer) > 0:
            self._send_frames(bytes(buffer))

    def _split_frame(self, frame: RakNetFrame) -> Generator[RakNetFrame, None, None]:
        split_packet_count = math.ceil(frame.payload_length // 8 / self._max_fragmented_payload_size)  # type: int
        split_packet_id = self._next_split_packet_id
        self._next_split_packet_id += 1
        payload = frame.payload
        for split_packet_index in range(split_packet_count):
            payload_fragment = payload[:self._max_fragmented_payload_size]
            fragment = raknet_frame_factory.create(
                RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                len(payload_fragment) * 8,
                frame.reliable_message_num,
                frame.message_ordering_index,
                frame.message_ordering_chanel,
                split_packet_count,
                split_packet_id,
                split_packet_index,
                payload_fragment
            )
            payload = payload[self._max_fragmented_payload_size:]
            yield fragment
