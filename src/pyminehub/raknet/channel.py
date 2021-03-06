from logging import getLogger
from typing import Dict, Iterator

from pyminehub.raknet.frame import RakNetFrame

__all__ = [
    'Channel'
]


_logger = getLogger(__name__)


class Channel:

    def __init__(self) -> None:
        self._cache = {}  # type: Dict[int, bytes]
        self._index = 0

    def __iter__(self) -> Iterator[bytes]:
        while self._index in self._cache:
            yield self._cache.pop(self._index)
            self._index += 1
        if len(self._cache) > 0:
            _logger.info(
                'Channel (%s) is cashing packets. The ordering index %d is missing.',
                id(self), self._index)

    def append(self, frame: RakNetFrame) -> None:
        if frame.message_ordering_index >= self._index:
            self._cache[frame.message_ordering_index] = frame.payload
