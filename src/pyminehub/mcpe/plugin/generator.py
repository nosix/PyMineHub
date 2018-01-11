from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import ChunkPosition


class ChunkGenerator:

    def create(self, position: ChunkPosition) -> Chunk:
        raise NotImplementedError()
