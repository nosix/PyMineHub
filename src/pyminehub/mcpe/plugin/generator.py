from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import ChunkPosition


class ChunkGeneratorPlugin:

    def create(self, position: ChunkPosition) -> Chunk:
        raise NotImplementedError()
