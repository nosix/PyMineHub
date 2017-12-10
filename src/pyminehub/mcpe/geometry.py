from typing import NamedTuple, Generic

from pyminehub.typing import NT


class Vector3(NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):
    pass


class ChunkPosition(NamedTuple('ChunkPosition', [('x', int), ('z', int)])):
    pass
