from typing import NamedTuple, Generic, TypeVar


T = TypeVar('T', int, float)


class Vector3(NamedTuple('Vector3', [('x', T), ('y', T), ('z', T)]), Generic[T]):
    pass


class ChunkPosition(NamedTuple('ChunkPosition', [('x', int), ('z', int)])):
    pass
