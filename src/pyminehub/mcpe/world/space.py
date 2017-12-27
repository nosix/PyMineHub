from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.geometry import Vector3, ChunkPositionWithDistance, ChunkPosition, to_local_position
from pyminehub.mcpe.world.database import DataBase
from pyminehub.mcpe.world.generator import SpaceGenerator


class Space:

    def __init__(self, generator: SpaceGenerator, db: DataBase) -> None:
        self._db = db
        self._generator = generator
        self._size = Vector3(32, 32, 32)

    def init_space(self):
        self._generator.generate_space(self._db, self._size.x, self._size.z)

    def get_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        # TODO check position
        return self._generator.generate_chunk(request)

    def get_height(self, position: Vector3) -> int:
        chunk_position = ChunkPosition.at(position)
        chunk = self.get_chunk(ChunkPositionWithDistance(0, chunk_position))
        position_in_chunk = to_local_position(position)
        return chunk.get_height(position_in_chunk.x, position_in_chunk.z)
