import math
import operator as _op
from numbers import Number
from typing import NamedTuple as _NamedTuple, Generic, Union, Iterator

from pyminehub.typevar import NT


class Vector3(_NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):

    area = property(lambda self: self.x * self.z)

    volume = property(lambda self: self.x * self.y * self.z)

    def _calc(self, f, value) -> 'Vector3':
        if isinstance(value, Number):
            return Vector3(f(self.x, value), f(self.y, value), f(self.z, value))
        else:
            if len(value) == 3:
                return Vector3(f(self.x, value[0]), f(self.y, value[1]), f(self.z, value[2]))
            if len(value) == 2:
                return Vector3(f(self.x, value[0]), self.y, f(self.z, value[1]))
        raise NotImplementedError()

    def __add__(self, value) -> 'Vector3':
        """
        >>> Vector3(1, 2, 3) + Vector3(4, 5, 6)
        Vector3(x=5, y=7, z=9)
        >>> Vector3(1, 2, 3) + 4
        Vector3(x=5, y=6, z=7)
        >>> Vector3(1, 2, 3) + (4, 5)
        Vector3(x=5, y=2, z=8)
        """
        return self._calc(_op.add, value)

    def __sub__(self, value) -> 'Vector3':
        """
        >>> Vector3(3, 2, 1) - Vector3(4, 5, 6)
        Vector3(x=-1, y=-3, z=-5)
        >>> Vector3(3, 2, 1) - 4
        Vector3(x=-1, y=-2, z=-3)
        >>> Vector3(3, 2, 1) - (4, 5)
        Vector3(x=-1, y=2, z=-4)
        """
        return self._calc(_op.sub, value)

    def __mul__(self, value) -> 'Vector3':
        return self._calc(_op.mul, value)

    def __truediv__(self, value) -> 'Vector3':
        return self._calc(_op.truediv, value)

    def __radd__(self, value) -> 'Vector3':
        return self._calc(_op.add, value)

    def __rsub__(self, value) -> 'Vector3':
        return self._calc(_op.sub, value)

    def __rmul__(self, value) -> 'Vector3':
        return self._calc(_op.mul, value)

    def distance(self, other: 'Vector3') -> Number:
        diff = self - other
        return math.sqrt(diff.x ** 2 + diff.z ** 2 + diff.y ** 2)

    def norm(self) -> 'Vector3':
        return self / self.distance(Vector3(0, 0, 0))

    def dot(self, other: 'Vector3', is_3d=True) -> Number:
        if is_3d:
            return self.x * other.x + self.z * other.z + self.y * other.y
        else:
            return self.x * other.x + self.z * other.z

    def cross(self, other: 'Vector3', is_3d=True) -> Union['Vector3', Number]:
        if is_3d:
            return Vector3(
                self.z * other.y - self.y * other.z,
                self.x * other.z - self.z * other.x,
                self.y * other.x - self.x * other.y)
        else:
            return self.x * other.z - self.z * other.x


class ChunkGeometry:

    SHAPE = Vector3(16, 128, 16)

    class Sub:
        """
        >>> ChunkGeometry.Sub.SHAPE.area
        256
        >>> ChunkGeometry.Sub.SHAPE.volume
        4096
        """

        SHAPE = Vector3(16, 16, 16)


class ChunkPosition(_NamedTuple('ChunkPosition', [('x', int), ('z', int)])):

    def __add__(self, other: tuple) -> 'ChunkPosition':
        return ChunkPosition(self.x + other[0], self.z + other[1])

    def __sub__(self, other: tuple) -> 'ChunkPosition':
        return ChunkPosition(self.x - other[0], self.z - other[1])


def to_chunk_position(v: Vector3) -> ChunkPosition:
    """
    >>> v = Vector3(256.0, 57.625, 256.0)
    >>> to_chunk_position(v)
    ChunkPosition(x=16, z=16)
    """
    return ChunkPosition(int(v.x // ChunkGeometry.SHAPE.x), int(v.z // ChunkGeometry.SHAPE.z))


ChunkPositionWithDistance = _NamedTuple('ChunkPositionWithDistance', [('distance', int), ('position', ChunkPosition)])


# TODO remove this
# radius = 8 : (16, 16), (15, 16), (16, 15), (15, 15), (17, 16), (14, 16), (17, 15), (14, 15), (16, 17)
#   (15, 17), (16, 14), (15, 14), (17, 17), (14, 17), (17, 14), (14, 14), (18, 16), (13, 16), (18, 15)
#   (13, 15), (16, 18), (15, 18), (16, 13), (15, 13), (18, 17), (13, 17), (18, 14), (13, 14), (17, 18)
#   (14, 18), (17, 13), (14, 13), (18, 18), (13, 18), (18, 13), (13, 13), (19, 16), (12, 16), (19, 15)
#   (12, 15), (16, 19), (15, 19), (16, 12), (15, 12), (19, 17), (12, 17), (19, 14), (12, 14), (17, 19)
#   (14, 19), (17, 12), (14, 12), (19, 18), ..., (19, 23), (12, 23), (19, 8), (12, 8)
def to_chunk_area(center: Vector3, radius: int) -> Iterator[ChunkPositionWithDistance]:
    """
    >>> len(list(to_chunk_area(Vector3(256.0, 57.625, 256.0), 8)))
    73
    """
    p = to_chunk_position(center)
    yield ChunkPositionWithDistance(0, p)
    for l in range(1, radius + 1):
        s = 2 * (l & 1) - 1
        for _ in range(l):
            p += (s, 0)
            yield ChunkPositionWithDistance(l, p)
        for _ in range(l):
            p += (0, s)
            yield ChunkPositionWithDistance(l, p)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
