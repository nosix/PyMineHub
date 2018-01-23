from pyminehub.mcpe.chunk import Chunk, create_empty_chunk
from pyminehub.mcpe.geometry import ChunkPosition
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin


class ChunkGeneratorPluginImpl(ChunkGeneratorPlugin):

    def create(self, position: ChunkPosition) -> Chunk:
        return create_empty_chunk()
