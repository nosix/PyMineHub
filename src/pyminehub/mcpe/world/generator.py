from typing import Iterator, Tuple

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.geometry import ChunkPosition, ChunkPositionWithDistance
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin

__all__ = [
    'SpaceGenerator',
    'BatchSpaceGenerator',
    'OnDemandSpaceGenerator',
]


class SpaceGenerator:

    def generate_space(self) -> None:
        raise NotImplementedError()

    def generate_chunk(self, position: ChunkPositionWithDistance) -> Chunk:
        raise NotImplementedError()


class BatchSpaceGenerator(SpaceGenerator):

    def __init__(self, generator_plugin: ChunkGeneratorPlugin, store: DataStore, size_x: int, size_z: int) -> None:
        self._store = store
        self._size_x = size_x
        self._size_z = size_z
        self._generator_plugin = generator_plugin

    def generate_space(self) -> None:
        if self._store.count_chunk() != self._size_x * self._size_z:
            for position, chunk in self._create_chunks(self._size_x, self._size_z):
                self._store.save_chunk(position, chunk, insert_only=True)

    def _create_chunks(self, size_x: int, size_z: int) -> Iterator[Tuple[ChunkPosition, Chunk]]:
        for x in range(size_x):
            for z in range(size_z):
                position = ChunkPosition(x, z)
                yield position, self._generator_plugin.create(position)

    def generate_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        chunk = self._store.load_chunk(request.position)
        if chunk is None:
            position = request.position % (self._size_x, self._size_z)
            return self._store.load_chunk(position)
        else:
            return chunk


class OnDemandSpaceGenerator(SpaceGenerator):

    def __init__(self, generator_plugin: ChunkGeneratorPlugin, store: DataStore) -> None:
        self._store = store
        self._generator_plugin = generator_plugin

    def generate_space(self) -> None:
        pass

    def generate_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        # TODO generate Chunk with a closer distance first
        chunk = self._store.load_chunk(request.position)
        if chunk is None:
            return self._generator_plugin.create(request.position)
        else:
            return chunk
