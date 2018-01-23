from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import ChunkPosition


__all__ = [
    'ChunkGeneratorPlugin'
]


class ChunkGeneratorPlugin:

    def create(self, position: ChunkPosition) -> Chunk:
        raise NotImplementedError()
