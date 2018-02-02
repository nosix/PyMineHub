from typing import Dict, List, Optional, Tuple

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.geometry import Vector3, Face, ChunkPositionWithDistance, ChunkPosition, to_local_position
from pyminehub.mcpe.value import Item, Block
from pyminehub.mcpe.world.block import BlockModel
from pyminehub.mcpe.world.generator import SpaceGenerator

__all__ = [
    'BLOCK_AIR',
    'Space'
]


BLOCK_AIR = Block(BlockType.AIR, 0)


class Space:

    def __init__(self, generator: SpaceGenerator, store: DataStore) -> None:
        self._store = store
        self._generator = generator
        self._size = Vector3(32, 32, 32)
        self._cache = {}  # type: Dict[ChunkPosition, Chunk]

    def init_space(self) -> None:
        self._generator.generate_space(self._size.x, self._size.z)

    def save(self) -> None:
        for position, chunk in self._cache.items():
            if chunk.is_updated:
                self._store.save_chunk(position, chunk)
                chunk.is_updated = False

    def get_chunk(self, request: ChunkPositionWithDistance) -> Chunk:
        if request.position in self._cache:
            return self._cache[request.position]
        chunk = self._generator.generate_chunk(request)
        # TODO save when cache is full
        self._cache[request.position] = chunk
        return chunk

    def _to_local(self, position: Vector3) -> Tuple[Chunk, Vector3]:
        chunk_position = ChunkPosition.at(position)
        chunk = self.get_chunk(ChunkPositionWithDistance(0, chunk_position))
        position_in_chunk = to_local_position(position)
        return chunk, position_in_chunk

    def get_height(self, position: Vector3) -> int:
        chunk, position_in_chunk = self._to_local(position)
        return chunk.get_height(position_in_chunk.x, position_in_chunk.z)

    def break_block(self, position: Vector3[int]) -> Optional[List[Item]]:
        """
        :param position: to break
        :return: None if it can't be broken, or spawned item list if can be broken
        """
        chunk, position_in_chunk = self._to_local(position)
        block = chunk.get_block(position_in_chunk)
        if block.type in (BlockType.AIR, BlockType.BEDROCK):
            return None
        chunk.set_block(position_in_chunk, BLOCK_AIR)
        return BlockModel(block).to_item()

    def put_block(
            self,
            position: Vector3[int],
            face: Face,
            block: Block
    ) -> Optional[Tuple[Vector3[int], Block]]:
        """Put a block

        :param position: position to attach block
        :param face: face to attach block
        :param block: block to be attached
        :return: updated position and block, or None if block can't be put
        """
        block_model = BlockModel(block)
        chunk, position_in_chunk = self._to_local(position)
        if not block_model.can_be_attached_on(chunk.get_block(position_in_chunk)):
            return None
        if block_model.has_layer:
            return self._update_layer(position, face, block_model)
        position = position + face.direction
        chunk, position_in_chunk = self._to_local(position)
        chunk.set_block(position_in_chunk, block)
        return position, block

    def _update_layer(
            self,
            position: Vector3[int],
            face: Face,
            block: BlockModel
    ) -> Optional[Tuple[Vector3[int], Block]]:
        """Put a stackable block

        :param position: position to attach block
        :param face: face to attach block
        :param block: block to be attached
        :return: updated position and block, or None if block can't be put
        """
        chunk, position_in_chunk = self._to_local(position)
        current_block = BlockModel(chunk.get_block(position_in_chunk))
        if block.type == current_block.type:
            new_block = current_block.stack_layer(block, face)
            if new_block is not None:
                if new_block != current_block.value:
                    chunk.set_block(position_in_chunk, new_block)
                    return position, new_block
                else:
                    return None
        position += face.direction
        chunk, position_in_chunk = self._to_local(position)
        target_block = BlockModel(chunk.get_block(position_in_chunk))
        if block.type == target_block.type:
            new_block = target_block.stack_layer(block, face.inverse)
            if new_block is not None:
                if new_block != target_block.value:
                    chunk.set_block(position_in_chunk, new_block)
                    return position, new_block
                else:
                    return None
        chunk.set_block(position_in_chunk, block.value)
        return position, block.value

    def revise_position(self, position: Vector3[float]) -> Vector3[float]:
        height = self.get_height(position)
        return position.copy(y=height)
