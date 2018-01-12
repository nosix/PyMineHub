from pyminehub.mcpe.plugin.default import *
from pyminehub.mcpe.plugin.generator import *
from pyminehub.mcpe.plugin.mob import *
from pyminehub.mcpe.plugin.player import *


class PluginLoader:

    @staticmethod
    def get_generator() -> ChunkGenerator:
        return DefaultChunkGenerator()

    @staticmethod
    def get_mob_processor() -> MobProcessor:
        return DefaultMobProcessor()

    @staticmethod
    def get_player_config() -> PlayerConfig:
        return DefaultPlayerConfig()


def get_plugin_loader() -> PluginLoader:
    return PluginLoader()
