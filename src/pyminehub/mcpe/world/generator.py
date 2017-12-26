from typing import Iterator, Tuple

from pyminehub.mcpe.chunk import Chunk, create_empty_chunk
from pyminehub.mcpe.geometry import ChunkPosition, ChunkPositionWithDistance
from pyminehub.mcpe.world.database import DataBase


class SpaceGenerator:

    def generate_space(self, db: DataBase, x_length: int, z_length: int) -> None:
        raise NotImplementedError()

    def generate_chunk(self, position: ChunkPositionWithDistance) -> Chunk:
        raise NotImplementedError()


class BatchSpaceGenerator(SpaceGenerator):

    def __init__(self) -> None:
        self._db = None  # type: DataBase

    def generate_space(self, db: DataBase, x_length: int, z_length: int) -> None:
        assert self._db is None
        self._db = db
        if self._db.count_chunk() != x_length * z_length:
            for position, chunk in self._create_chunks(x_length, z_length):
                self._db.save_chunk(position, chunk, insert_only=True)

    @staticmethod
    def _create_chunks(x_length: int, z_length: int) -> Iterator[Tuple[ChunkPosition, Chunk]]:
        for x in range(x_length):
            for z in range(z_length):
                yield ChunkPosition(x, z), create_empty_chunk()

    def generate_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        return self._db.load_chunk(request.position)
