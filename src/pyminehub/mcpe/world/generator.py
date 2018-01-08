from typing import Iterator, Tuple

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import ChunkPosition, ChunkPositionWithDistance
from pyminehub.mcpe.plugin import Generator
from pyminehub.mcpe.world.database import DataBase


class SpaceGenerator:

    def generate_space(self, db: DataBase, x_length: int, z_length: int) -> None:
        raise NotImplementedError()

    def generate_chunk(self, position: ChunkPositionWithDistance) -> Chunk:
        raise NotImplementedError()


class BatchSpaceGenerator(SpaceGenerator):

    def __init__(self, generator_plugin: Generator) -> None:
        self._db = None  # type: DataBase
        self._x_length = 0
        self._z_length = 0
        self._generator_plugin = generator_plugin

    def generate_space(self, db: DataBase, x_length: int, z_length: int) -> None:
        assert self._db is None
        self._db = db
        self._x_length = x_length
        self._z_length = z_length
        if self._db.count_chunk() != x_length * z_length:
            for position, chunk in self._create_chunks(x_length, z_length):
                self._db.save_chunk(position, chunk, insert_only=True)

    def _create_chunks(self, x_length: int, z_length: int) -> Iterator[Tuple[ChunkPosition, Chunk]]:
        for x in range(x_length):
            for z in range(z_length):
                position = ChunkPosition(x, z)
                yield position, self._generator_plugin.create(position)

    def generate_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        position = request.position % (self._x_length, self._z_length)
        return self._db.load_chunk(position)
