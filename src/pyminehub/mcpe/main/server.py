def configure_log(enable_packet_debug=False, enable_world_debug=False, enable_generator_debug=False) -> None:
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

    import logging
    from logging.handlers import RotatingFileHandler
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    file = RotatingFileHandler(
        log_file_name, mode='w', maxBytes=int(max_bytes * 1024 * 1024), backupCount=backup_count, encoding='utf-8')
    file.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, handlers=(stream, file))

    levels = {}
    if enable_packet_debug:
        levels['pyminehub.raknet.server'] = logging.DEBUG
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


def run() -> None:
    import asyncio
    from pyminehub.mcpe.network import MCPEHandler
    from pyminehub.mcpe.world import run as run_world
    from pyminehub.raknet import run as run_raknet

    loop = asyncio.get_event_loop()
    proxy = run_world(loop)
    transport = run_raknet(loop, MCPEHandler(proxy))
    transport.close()
    loop.close()


if __name__ == '__main__':
    configure_log()
    run()
