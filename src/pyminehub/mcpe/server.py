from pyminehub.mcpe.network import MCPEHandler
from pyminehub.mcpe.world import run as run_world
from pyminehub.raknet import run as run_raknet


def run() -> None:
    proxy = run_world()
    run_raknet(MCPEHandler(proxy))


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
