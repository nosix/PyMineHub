from typing import Iterator, Tuple

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.geometry import ChunkPosition, ChunkPositionWithDistance
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin

__all__ = [
    'SpaceGenerator',
    'BatchSpaceGenerator'
]


class SpaceGenerator:

    def generate_space(self, x_length: int, z_length: int) -> None:
        raise NotImplementedError()

    def generate_chunk(self, position: ChunkPositionWithDistance) -> Chunk:
        raise NotImplementedError()


class BatchSpaceGenerator(SpaceGenerator):

    def __init__(self, generator_plugin: ChunkGeneratorPlugin, store: DataStore) -> None:
        self._store = store
        self._x_length = 0
        self._z_length = 0
        self._generator_plugin = generator_plugin

    def generate_space(self, x_length: int, z_length: int) -> None:
        self._x_length = x_length
        self._z_length = z_length
        if self._store.count_chunk() != x_length * z_length:
            for position, chunk in self._create_chunks(x_length, z_length):
                self._store.save_chunk(position, chunk, insert_only=True)

    def _create_chunks(self, x_length: int, z_length: int) -> Iterator[Tuple[ChunkPosition, Chunk]]:
        for x in range(x_length):
            for z in range(z_length):
                position = ChunkPosition(x, z)
                yield position, self._generator_plugin.create(position)

    def generate_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        position = request.position % (self._x_length, self._z_length)
        return self._store.load_chunk(position)
