from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import Vector3, ChunkPositionWithDistance
from pyminehub.mcpe.world.database import DataBase
from pyminehub.mcpe.world.generator import SpaceGenerator


class Space:

    def __init__(self, generator: SpaceGenerator, db: DataBase) -> None:
        self._db = db
        self._generator = generator
        self._size = Vector3(256, 256, 256)

    def init_space(self):
        self._generator.generate_space(self._db, self._size.x, self._size.z)

    def get_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        # TODO check position
        return self._generator.generate_chunk(request)
