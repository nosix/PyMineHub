from pyminehub.mcpe.network import MCPEHandler
from pyminehub.raknet import run as run_raknet


def run() -> None:
    run_raknet(MCPEHandler())


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    run()
