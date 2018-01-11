from logging import getLogger

from pyminehub.mcpe.chunk import *
from pyminehub.mcpe.plugin.generator import *

_logger = getLogger(__name__)


class DefaultChunkGenerator(ChunkGenerator):

    def __init__(self) -> None:
        def set_data(x: int, z: int) -> None:
            y = 0
            chunk.set_block(Vector3(x, y, z), BlockType.BEDROCK, 0)
            y += 1
            while y < height - 6:
                chunk.set_block(Vector3(x, y, z), BlockType.STONE, 0)
                y += 1
            while y < height - 1:
                chunk.set_block(Vector3(x, y, z), BlockType.STONE, 0)
                y += 1
            chunk.set_block(Vector3(x, y, z), BlockType.GRASS, 0)
            y += 1
            assert y == height
            chunk.set_height(x, z, height)
            chunk.set_biome_id(x, z, BiomeType.PLAINS)

        height = 63
        chunk = Chunk(tuple(), EMPTY_HEIGHT_MAP, EMPTY_BIOME_ID, tuple(), tuple())
        foreach_xz(set_data)
        self._default_chunk = chunk

    def create(self, position: ChunkPosition) -> Chunk:
        _logger.debug('Create chunk at %s', position)
        return self._default_chunk.copy()
