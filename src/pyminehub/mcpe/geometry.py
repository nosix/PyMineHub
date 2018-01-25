import functools
import math
import operator as _op
from enum import Enum
from numbers import Number
from typing import Generic, Iterator, NamedTuple

from pyminehub.typevar import NT

__all__ = [
    'Vector3',
    'Face',
    'OrientedBoundingBox',
    'ChunkGeometry',
    'ChunkPosition',
    'ChunkPositionWithDistance',
    'to_chunk_area',
    'to_local_position',
    'revise_angle'
]


class Vector3(NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):
    """
    x : west - <=> + east
    y : downward - <=> + upward
    z : north - <=> + south
    """

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

    def astype(self, cls: type) -> 'Vector3':
        """
        >>> Vector3(1.1, 2.2, 3.3).astype(int)
        Vector3(x=1, y=2, z=3)
        """
        return Vector3(cls(self.x), cls(self.y), cls(self.z))

    def distance(self, other: 'Vector3') -> Number:
        """
        >>> Vector3(4, 4, 4).distance(Vector3(2, 2, 2)) == math.sqrt(12)
        True
        """
        diff = self - other
        return math.sqrt(diff.x ** 2 + diff.z ** 2 + diff.y ** 2)

    def distance_2d(self, other: 'Vector3') -> Number:
        """
        >>> Vector3(4, 4, 4).distance_2d(Vector3(2, 2, 2)) == math.sqrt(8)
        True
        """
        diff = self - other
        return math.sqrt(diff.x ** 2 + diff.z ** 2)

    def norm(self) -> 'Vector3':
        """
        >>> Vector3(2, 2, 2).norm() == Vector3(2 / math.sqrt(12), 2 / math.sqrt(12), 2 / math.sqrt(12))
        True
        """
        return self / self.distance(Vector3(0, 0, 0))

    def norm_2d(self) -> 'Vector3':
        """
        >>> Vector3(2, 2, 2).norm_2d() == Vector3(2 / math.sqrt(8), 0, 2 / math.sqrt(8))
        True
        """
        return self.copy(y=0) / self.distance_2d(Vector3(0, 0, 0))

    def dot(self, other: 'Vector3') -> Number:
        return self.x * other.x + self.z * other.z + self.y * other.y

    def dot_2d(self, other: 'Vector3') -> Number:
        return self.x * other.x + self.z * other.z

    def cross(self, other: 'Vector3') -> 'Vector3':
        return Vector3(
            self.z * other.y - self.y * other.z,
            self.x * other.z - self.z * other.x,
            self.y * other.x - self.x * other.y)

    def cross_2d(self, other: 'Vector3') -> Number:
        return self.x * other.z - self.z * other.x

    def rotate(self, yaw: float) -> 'Vector3':
        """
               (180)
                z-
        (90) x-    x+ (270)
                z+
               (0)

        >>> Vector3(1, 0, 0).rotate(90).astype(int)
        Vector3(x=0, y=0, z=1)
        >>> Vector3(0, 0, 1).rotate(90).astype(int)
        Vector3(x=-1, y=0, z=0)
        >>> Vector3(1, 0, 0).rotate(-90).astype(int)
        Vector3(x=0, y=0, z=-1)
        >>> Vector3(0, 0, -1).rotate(-90).astype(int)
        Vector3(x=-1, y=0, z=0)

        :param yaw: angle of rotation
        :return: rotated vector
        """
        rad = math.radians(yaw)
        x = - self.z * math.sin(rad) + self.x * math.cos(rad)
        z = self.z * math.cos(rad) + self.x * math.sin(rad)
        return Vector3(x, self.y, z)


class Face(Enum):
    NONE = (-1, Vector3(0, 0, 0))
    BOTTOM = (0, Vector3(0, -1, 0))
    TOP = (1, Vector3(0, 1, 0))
    SOUTH = (2, Vector3(0, 0, -1))
    NORTH = (3, Vector3(0, 0, 1))
    EAST = (4, Vector3(-1, 0, 0))
    WEST = (5, Vector3(1, 0, 0))

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

    @property
    def inverse(self) -> 'Face':
        return Face(self.value ^ 1) if self is not self.NONE else self

    @classmethod
    def by_yaw(cls, yaw: float) -> 'Face':
        """Return the face the player is looking at.

               (0)
                3
        (270) 5   4 (90)
                2
              (180)

        >>> Face.by_yaw(0)
        <Face.NORTH: 3>
        >>> Face.by_yaw(90)
        <Face.EAST: 4>
        >>> Face.by_yaw(180)
        <Face.SOUTH: 2>
        >>> Face.by_yaw(270)
        <Face.WEST: 5>
        """
        assert 0 <= yaw < 360
        if 45 <= yaw <= 135:
            return cls.EAST
        if 225 <= yaw <= 315:
            return cls.WEST
        if 135 < yaw < 225:
            return cls.SOUTH
        else:
            return cls.NORTH

    @classmethod
    def by_pitch(cls, pitch: float) -> 'Face':
        """Return the face the player is looking at.

        >>> Face.by_pitch(90)
        <Face.TOP: 1>
        >>> Face.by_pitch(270)
        <Face.BOTTOM: 0>
        """
        assert 0 <= pitch < 360
        return cls.TOP if 0 <= pitch < 180 else cls.BOTTOM

    @classmethod
    def by_angle(cls, yaw: float, pitch: float) -> 'Face':
        """Return the face the player is looking at.

        >>> Face.by_angle(0, 60)
        <Face.BOTTOM: 0>
        >>> Face.by_angle(0, 30)
        <Face.NORTH: 3>
        """
        assert 0 <= pitch < 360
        if 45 <= pitch < 135:
            return cls.BOTTOM
        if 225 <= pitch < 315:
            return cls.TOP
        return cls.by_yaw(yaw)


class OrientedBoundingBox(NamedTuple('OrientedBoundingBox', [
    ('origin', Vector3[float]),
    ('forward', Vector3[float]),
    ('right', Vector3[float]),
    ('upward', Vector3[float])
])):

    @classmethod
    def create(cls, center_bottom: Vector3[float], size: Vector3[float], yaw: float) -> 'OrientedBoundingBox':
        half = size / 2.0
        origin = center_bottom + Vector3(0.0, half.y, 0.0)
        forward = Vector3(0.0, 0.0, half.z).rotate(yaw)
        right = Vector3(-half.x, 0.0, 0.0).rotate(yaw)
        upward = Vector3(0.0, half.y, 0.0)
        return OrientedBoundingBox(origin, forward, right, upward)

    @staticmethod
    def _has_collision_xz(origin, vec_a1, vec_a2, vec_b1, vec_b2) -> bool:
        vec_l = vec_a1.norm_2d()
        rb = abs(vec_l.dot_2d(vec_b1)) + abs(vec_l.dot_2d(vec_b2))
        ra = vec_a1.distance_2d(Vector3(0, 0, 0))
        interval = abs(vec_l.dot_2d(origin))
        return interval <= ra + rb

    @staticmethod
    def _has_collision_y(origin, vec_a, vec_b) -> bool:
        return not abs(origin.y) > vec_a.y + vec_b.y

    def has_collision(self, other: 'OrientedBoundingBox') -> bool:
        origin = self.origin - other.origin
        has_collision_xz = functools.partial(self._has_collision_xz, origin)
        return (has_collision_xz(self.forward, self.right, other.forward, other.right) and
                has_collision_xz(self.right, self.forward, other.right, other.forward) and
                has_collision_xz(other.forward, other.right, self.forward, self.right) and
                has_collision_xz(other.right, other.forward, self.right, self.forward) and
                self._has_collision_y(origin, self.upward, other.upward))


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


class ChunkPosition(NamedTuple('ChunkPosition', [('x', int), ('z', int)])):

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


ChunkPositionWithDistance = NamedTuple('ChunkPositionWithDistance', [('distance', int), ('position', ChunkPosition)])


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


def revise_angle(value: float) -> float:
    """
    >>> revise_angle(0)
    0
    >>> revise_angle(540)
    180
    >>> revise_angle(-90)
    270
    >>> revise_angle(-180)
    180
    >>> revise_angle(-540)
    180
    """
    return value % 360


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
