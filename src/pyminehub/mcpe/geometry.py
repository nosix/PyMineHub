from typing import NamedTuple as _NamedTuple, Generic

from pyminehub.typing import NT


class Vector3(_NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):
    pass


class ChunkPosition(_NamedTuple('ChunkPosition', [('x', int), ('z', int)])):
    pass
