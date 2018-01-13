import importlib
import sys
from logging import getLogger
from pathlib import Path

from pyminehub.mcpe.plugin.default import *
from pyminehub.mcpe.plugin.generator import *
from pyminehub.mcpe.plugin.mob import *
from pyminehub.mcpe.plugin.player import *

_logger = getLogger(__name__)


_PLUGIN_ROOT_ENV_NAME = 'PMH_PLUGIN_ROOT'


class PluginLoader:

    def __init__(self, plugin_directory: str) -> None:
        """
        >>> loader = PluginLoader('')
        >>> isinstance(loader.generator, DefaultChunkGenerator)
        True
        >>> loader = PluginLoader('../../../../plugin')
        >>> isinstance(loader.generator, DefaultChunkGenerator)
        False
        """
        self._generator = DefaultChunkGenerator()
        self._mob_processor = DefaultMobProcessor()
        self._player_config = DefaultPlayerConfig()
        if plugin_directory:
            self._load_plugin(plugin_directory)
        else:
            _logger.info('Plugin is disabled.')

    def _load_plugin(self, plugin_directory: str) -> None:
        plugin_root = Path(plugin_directory)
        if not plugin_root.exists():
            _logger.info('Plugin directory "%s" is not found.', plugin_directory)
            return
        _logger.info('Plugin is loaded from directory "%s"].', plugin_directory)
        sys.path.append(str(plugin_root))
        for node in plugin_root.iterdir():
            plugin_module = importlib.import_module(str(node.name))
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if not isinstance(attr, type):
                    continue
                if issubclass(attr, ChunkGenerator):
                    self._generator = attr()
                if issubclass(attr, MobProcessor):
                    self._generator = attr()
                if issubclass(attr, PlayerConfig):
                    self._generator = attr()

    @property
    def generator(self) -> ChunkGenerator:
        return self._generator

    @property
    def mob_processor(self) -> MobProcessor:
        return self._mob_processor

    @property
    def player_config(self) -> PlayerConfig:
        return self._player_config


def get_plugin_loader() -> PluginLoader:
    import os
    plugin_root = os.getenv(_PLUGIN_ROOT_ENV_NAME, 'plugin')
    if _PLUGIN_ROOT_ENV_NAME in os.environ:
        _logger.info('%s=%s', _PLUGIN_ROOT_ENV_NAME, plugin_root)
    return PluginLoader(plugin_root)


if __name__ == '__main__':
    sys.path.pop(0)  # remove current directory
    import os
    os.chdir(Path(__file__).parent)
    import doctest
    doctest_result = doctest.testmod()
