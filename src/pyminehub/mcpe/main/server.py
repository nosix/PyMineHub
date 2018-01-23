import asyncio
import logging


__all__ = [
    'configure_log',
    'run'
]


def configure_log(
        enable_packet_debug=False,
        enable_world_debug=False,
        enable_generator_debug=False,
        disable_chunk_debug=False
) -> None:
    log_file_name = 'server.log'
    backup_count = 10
    max_bytes = 1  # MB

    import os

    def remove_file(path: str):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    remove_file(log_file_name)
    for i in range(backup_count):
        remove_file('{}.{}'.format(log_file_name, i+1))

    from logging.handlers import RotatingFileHandler
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    file = RotatingFileHandler(
        log_file_name, mode='w', maxBytes=int(max_bytes * 1024 * 1024), backupCount=backup_count, encoding='utf-8')
    file.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, handlers=(stream, file))

    levels = {}
    if enable_packet_debug:
        levels['pyminehub.raknet.protocol'] = logging.DEBUG
        levels['pyminehub.raknet.session'] = logging.DEBUG
        levels['pyminehub.mcpe.network.handler'] = logging.DEBUG
        levels['pyminehub.mcpe.network.queue'] = logging.DEBUG
        levels['pyminehub.raknet.sending'] = logging.DEBUG
    if enable_world_debug:
        levels['pyminehub.mcpe.world.server'] = logging.DEBUG
    if enable_generator_debug:
        levels['pyminehub.mcpe.plugin.default.generator'] = logging.DEBUG

    if len(levels) > 0:
        from pyminehub.config import set_config
        set_config(max_log_length=None)
        for name, level in levels.items():
            logging.getLogger(name).setLevel(level)

    if disable_chunk_debug:

        def log_filter(record) -> bool:
            packet_str = str(record.args[0])
            return not packet_str.startswith('FullChunkLoaded') and not packet_str.startswith('RequestChunk')

        logging.getLogger('pyminehub.mcpe.world.server').addFilter(log_filter)


def run() -> None:
    from pyminehub.mcpe.network import MCPEServerHandler
    from pyminehub.mcpe.datastore import create_data_store
    from pyminehub.mcpe.command import CommandRegistry
    from pyminehub.mcpe.plugin.loader import get_plugin_loader
    from pyminehub.mcpe.world import run as run_world
    from pyminehub.raknet import raknet_server
    from pyminehub.config import ConfigKey, print_config

    print_config(
        ConfigKey.SERVER_PORT,
        ConfigKey.SEED,
        ConfigKey.SPAWN_MOB,
        ConfigKey.WORLD_NAME,
        ConfigKey.GAME_MODE,
    )

    loop = asyncio.get_event_loop()
    store = create_data_store()
    store.delete_all()
    command = CommandRegistry()
    proxy = run_world(store, get_plugin_loader(command))
    with raknet_server(MCPEServerHandler(proxy, command)):
        pass
    loop.close()


if __name__ == '__main__':
    configure_log()
    run()
