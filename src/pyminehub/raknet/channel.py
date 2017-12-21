from typing import Dict, Iterator

from pyminehub.raknet.frame import RakNetFrame


class Channel:

    def __init__(self) -> None:
        self._cache = {}  # type: Dict[int, bytes]
        self._index = 0

    def __iter__(self) -> Iterator[bytes]:
        while self._index in self._cache:
            yield self._cache.pop(self._index)
            self._index += 1

    def append(self, frame: RakNetFrame) -> None:
        self._cache[frame.message_ordering_index] = frame.payload
