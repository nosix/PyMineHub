import importlib
import sys
from logging import getLogger
from pathlib import Path
from typing import Optional

from pyminehub.mcpe.command import CommandRegistry
from pyminehub.mcpe.plugin.command import ExtraCommandPlugin
from pyminehub.mcpe.plugin.default import *
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin
from pyminehub.mcpe.plugin.mob import MobProcessorPlugin
from pyminehub.mcpe.plugin.player import PlayerConfigPlugin

__all__ = [
    'PluginLoader',
    'get_plugin_loader'
]


_logger = getLogger(__name__)


_PLUGIN_ROOT_ENV_NAME = 'PMH_PLUGIN_ROOT'

_PLUGIN_INTERFACES = (
    ChunkGeneratorPlugin,
    MobProcessorPlugin,
    PlayerConfigPlugin,
    ExtraCommandPlugin
)


class PluginLoader:

    def __init__(self, plugin_directory: str, command: Optional[CommandRegistry]=None) -> None:
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
            self._load_plugin(plugin_directory, command)
        else:
            _logger.info('Plugin is disabled.')

    def _load_plugin(self, plugin_directory: str, command: Optional[CommandRegistry]) -> None:
        plugin_root = Path(plugin_directory)
        if not plugin_root.exists():
            _logger.info('Plugin directory "%s" is not found.', plugin_directory)
            return
        _logger.info('Plugin is loaded from directory "%s".', plugin_directory)
        sys.path.append(str(plugin_root))
        for node in plugin_root.iterdir():
            plugin_module = importlib.import_module(str(node.name))
            attr_names = plugin_module.__all__ if hasattr(plugin_module, '__all__') else dir(plugin_module)
            for attr_name in attr_names:
                attr = getattr(plugin_module, attr_name)
                if not isinstance(attr, type):
                    continue
                if issubclass(attr, _PLUGIN_INTERFACES):
                    instance = attr()
                    if issubclass(attr, ChunkGeneratorPlugin):
                        self._generator = instance
                        _logger.info('%s overrode ChunkGeneratorPlugin.', attr.__name__)
                    if issubclass(attr, MobProcessorPlugin):
                        self._mob_processor = instance
                        _logger.info('%s overrode MobProcessorPlugin.', attr.__name__)
                    if issubclass(attr, PlayerConfigPlugin):
                        self._player_config = instance
                        _logger.info('%s overrode PlayerConfigPlugin.', attr.__name__)
                    if command is not None and issubclass(attr, ExtraCommandPlugin):
                        processor = instance.processor
                        command.register_command_processor(processor)
                        _logger.info('%s was registered into CommandRegistry.', type(processor).__name__)

    @property
    def generator(self) -> ChunkGeneratorPlugin:
        return self._generator

    @property
    def mob_processor(self) -> MobProcessorPlugin:
        return self._mob_processor

    @property
    def player_config(self) -> PlayerConfigPlugin:
        return self._player_config


def get_plugin_loader(command: Optional[CommandRegistry]=None) -> PluginLoader:
    import os
    plugin_root = os.getenv(_PLUGIN_ROOT_ENV_NAME, 'plugin')
    if _PLUGIN_ROOT_ENV_NAME in os.environ:
        _logger.info('%s=%s', _PLUGIN_ROOT_ENV_NAME, plugin_root)
    return PluginLoader(plugin_root, command)


if __name__ == '__main__':
    sys.path.pop(0)  # remove current directory
    import os
    os.chdir(str(Path(__file__).parent))
    import doctest
    doctest_result = doctest.testmod()
