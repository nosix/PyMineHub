from pyminehub.mcpe.chunk import *
from pyminehub.mcpe.plugin.generator import *


class ChunkGeneratorImpl(ChunkGenerator):

    def create(self, position: ChunkPosition) -> Chunk:
        return create_empty_chunk()
