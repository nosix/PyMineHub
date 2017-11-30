from typing import Dict, Optional


class _Entry:

    def __init__(self, split_count: int):
        self._count = split_count
        self._payload = {}  # type: Dict[int, bytes]

    def __setitem__(self, index: int, value: bytes):
        self._payload[index] = value

    def has_all_payload(self) -> bool:
        return len(self._payload) == self._count

    def get_payload(self):
        assert self.has_all_payload()
        payload = bytearray()
        for i in range(self._count):
            payload.extend(self._payload[i])
        return bytes(payload)


class MessageFragment:

    def __init__(self):
        self._entries = {}  # type: Dict[int, _Entry]

    def append(self, split_id: int, split_count: int, split_index: int, payload: bytes) -> None:
        if split_id not in self._entries:
            self._entries[split_id] = _Entry(split_count)
        self._entries[split_id][split_index] = payload

    def pop(self, split_id: int) -> Optional[bytes]:
        assert split_id in self._entries
        entry = self._entries[split_id]
        if entry.has_all_payload():
            del self._entries[split_id]
            return entry.get_payload()
        else:
            return None
