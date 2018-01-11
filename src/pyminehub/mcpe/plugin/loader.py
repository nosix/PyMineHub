from pyminehub.mcpe.plugin.default import *
from pyminehub.mcpe.plugin.generator import *
from pyminehub.mcpe.plugin.mob import *


def get_generator() -> ChunkGenerator:
    return DefaultChunkGenerator()


def get_mob_processor() -> MobProcessor:
    return DefaultMobProcessor()
