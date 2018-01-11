from pyminehub.mcpe.plugin.default import DefaultChunkGenerator
from pyminehub.mcpe.plugin.generator import ChunkGenerator


def get_generator() -> ChunkGenerator:
    return DefaultChunkGenerator()
