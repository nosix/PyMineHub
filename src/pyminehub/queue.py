import itertools
from heapq import heappush, heappop
from queue import Empty
from typing import Callable, Dict, Generic, List, Optional, Tuple, TypeVar


__all__ = [
    'UpdatablePriorityQueue'
]


_UPPT = TypeVar('UPPT', int, float)
_UPKT = TypeVar('UPKT')
_UPTT = TypeVar('UPTT')


class UpdatablePriorityQueue(Generic[_UPPT, _UPKT, _UPTT]):

    def __init__(self, key_producer: Callable[[_UPTT], Optional[_UPKT]]) -> None:
        self._key_producer = key_producer
        self._heap_queue = []  # type: List[List[_UPPT, int, _UPTT]]
        self._entry_finder = {}  # type: Dict[_UPKT, _UPTT]
        self._counter = itertools.count()

    def pop(self, key: _UPKT) -> _UPTT:
        """Remove a task of the specified key from this queue and get the task."""
        entry = self._entry_finder.pop(key)
        task = entry[-1]
        entry[-1] = None
        return task

    def remove(self, task: _UPTT) -> None:
        """Remove the task from this queue."""
        key = self._key_producer(task)
        self.pop(key)

    def put(self, priority: _UPPT, task: _UPTT) -> None:
        """Put the task into this queue."""
        entry = [priority, next(self._counter), task]
        heappush(self._heap_queue, entry)

        key = self._key_producer(task)
        if key is not None:
            if key in self._entry_finder:
                self.remove(task)
            self._entry_finder[key] = entry

    def get(self) -> Tuple[_UPPT, _UPTT]:
        """Get a minimum priority task from this queue or raise Empty when queue is empty."""
        while self._heap_queue:
            priority, count, task = heappop(self._heap_queue)
            if task is None:
                continue
            key = self._key_producer(task)
            if key is not None:
                del self._entry_finder[key]
            return priority, task
        raise Empty()
