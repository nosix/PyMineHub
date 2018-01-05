import math
import operator as _op
from enum import Enum
from numbers import Number
from typing import NamedTuple as _NamedTuple, Generic, Union, Iterator

from pyminehub.typevar import NT


class Vector3(_NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):

    def copy(self, x: NT=None, y: NT=None, z: NT=None) -> 'Vector3[NT]':
        """
        >>> v = Vector3(1, 2, 3)
        >>> v.copy()
        Vector3(x=1, y=2, z=3)
        >>> v.copy(y=4)
        Vector3(x=1, y=4, z=3)
        """
        return Vector3(self.x if x is None else x, self.y if y is None else y, self.z if z is None else z)

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
        return NotImplemented

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


class Face(Enum):
    BOTTOM = (0, Vector3(0, -1, 0))
    UPPER = (1, Vector3(0, 1, 0))
    NORTH = (2, Vector3(0, 0, -1))
    SOUTH = (3, Vector3(0, 0, 1))
    WEST = (4, Vector3(-1, 0, 0))
    EAST = (5, Vector3(1, 0, 0))

    def __new__(cls, value: int, direction: Vector3[int]) -> 'Face':
        """
        >>> Face.BOTTOM
        <Face.BOTTOM: 0>
        >>> Face(0)
        <Face.BOTTOM: 0>
        >>> Face['BOTTOM']
        <Face.BOTTOM: 0>
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj._direction = direction
        return obj

    @property
    def direction(self) -> Vector3[int]:
        return self._direction

    @classmethod
    def by_yaw(cls, yaw: float) -> 'Face':
        """Return the face the player is looking at.

                   (0)
                    3
            (270) 5   4 (90)
                    2
                  (180)

        >>> Face.by_yaw(0)
        <Face.SOUTH: 3>
        """
        if 45 <= yaw <= 135:
            return cls.WEST
        if 225 <= yaw <= 315:
            return cls.EAST
        if 135 < yaw < 225:
            return cls.NORTH
        else:
            return cls.SOUTH

    @classmethod
    def by_pitch(cls, pitch: float) -> 'Face':
        """Return the face the player is looking at.

        >>> Face.by_pitch(1)
        <Face.BOTTOM: 0>
        """
        return cls.UPPER if pitch < 0 else cls.BOTTOM

    @classmethod
    def by_angle(cls, yaw: float, pitch: float) -> 'Face':
        """Return the face the player is looking at.

        >>> Face.by_angle(0, 60)
        <Face.BOTTOM: 0>
        >>> Face.by_angle(0, 30)
        <Face.SOUTH: 3>
        """
        if pitch > 45:
            return cls.BOTTOM
        if pitch < -45:
            return cls.UPPER
        return cls.by_yaw(yaw)


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

    def __mod__(self, other: tuple) -> 'ChunkPosition':
        """
        >>> ChunkPosition(99, -199) % (100, 100)
        ChunkPosition(x=99, z=1)
        """
        return ChunkPosition(self.x % other[0], self.z % other[1])

    @staticmethod
    def at(position: Vector3) -> 'ChunkPosition':
        """
        >>> v = Vector3(256.0, 57.625, 266.5)
        >>> ChunkPosition.at(v)
        ChunkPosition(x=16, z=16)
        """
        return ChunkPosition(int(position.x // ChunkGeometry.SHAPE.x), int(position.z // ChunkGeometry.SHAPE.z))


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
    p = ChunkPosition.at(center)
    yield ChunkPositionWithDistance(0, p)
    for l in range(1, radius + 1):
        s = 2 * (l & 1) - 1
        for _ in range(l):
            p += (s, 0)
            yield ChunkPositionWithDistance(l, p)
        for _ in range(l):
            p += (0, s)
            yield ChunkPositionWithDistance(l, p)


def to_local_position(position: Vector3) -> Vector3[int]:
    """Convert the position to a position in a chunk.
    >>> v = Vector3(256.0, 57.625, 266.5)
    >>> to_local_position(v)
    Vector3(x=0, y=57, z=10)
    """
    return Vector3(
        int(position.x % ChunkGeometry.SHAPE.x),
        int(position.y),
        int(position.z % ChunkGeometry.SHAPE.z))


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
