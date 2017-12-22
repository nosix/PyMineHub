from typing import NamedTuple as _NamedTuple, Generic

from pyminehub.typevar import NT


class Vector3(_NamedTuple('Vector3', [('x', NT), ('y', NT), ('z', NT)]), Generic[NT]):
    area = property(lambda self: self.x * self.z)
    volume = property(lambda self: self.x * self.y * self.z)


class ChunkPosition(_NamedTuple('ChunkPosition', [('x', int), ('z', int)])):
    pass


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


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
