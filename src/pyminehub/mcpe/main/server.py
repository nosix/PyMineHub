import asyncio

from pyminehub.mcpe.network import MCPEHandler
from pyminehub.mcpe.world import run as run_world
from pyminehub.raknet import run as run_raknet


def run() -> None:
    loop = asyncio.get_event_loop()
    proxy = run_world(loop)
    transport = run_raknet(loop, MCPEHandler(proxy))
    try:
        loop.run_forever()
        pass
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()
        loop.close()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
