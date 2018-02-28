from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import ChunkPosition


__all__ = [
    'ChunkGeneratorPlugin'
]


class ChunkGeneratorPlugin:

    def create(self, position: ChunkPosition) -> Chunk:
        """Create chunk of specified position.

        :param position: position to generate chunk at
        :return: see `pyminehub.mcpe.chunk`
        """
        raise NotImplementedError()
