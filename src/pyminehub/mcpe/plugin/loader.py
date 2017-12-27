from pyminehub.mcpe.plugin.default import DefaultGenerator
from pyminehub.mcpe.plugin.generator import Generator


def get_generator() -> Generator:
    return DefaultGenerator()
