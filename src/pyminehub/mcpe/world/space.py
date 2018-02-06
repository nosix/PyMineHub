from functools import partial
from typing import Callable, Dict, Iterator, List, NamedTuple, Tuple

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.geometry import Vector3, Face, ChunkPositionWithDistance, ChunkPosition, to_local_position
from pyminehub.mcpe.value import Item, Block
from pyminehub.mcpe.world.block import CompositeBlock, PlacedBlock
from pyminehub.mcpe.world.generator import SpaceGenerator

__all__ = [
    'BLOCK_AIR',
    'Space',
]


BLOCK_AIR = Block(BlockType.AIR, 0)

_UpdateAction = NamedTuple('UpdateAction', [
    ('block', PlacedBlock),
    ('update', Callable[[], None])
])


class _Transaction:

    def __init__(self) -> None:
        self._action = []  # type: List[_UpdateAction]

    def append(self, position: Vector3[int], block: Block, update: Callable[[], None]) -> None:
        self._action.append(_UpdateAction(PlacedBlock(position, block), update))

    def clear(self) -> None:
        self._action.clear()

    def commit(self) -> Iterator[PlacedBlock]:
        for action in self._action:
            action.update()
            yield action.block
        self._action.clear()


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

    def break_block(self, position: Vector3[int]) -> Tuple[List[PlacedBlock], List[Item]]:
        """
        :param position: to break
        :return: updated position and block | spawned item list
        """
        chunk, position_in_chunk = self._to_local(position)
        block = chunk.get_block(position_in_chunk)
        broken_block = CompositeBlock(block)
        if not broken_block.can_be_broken:
            return [], []
        transaction = _Transaction()
        update = partial(chunk.set_block, position_in_chunk, BLOCK_AIR)
        transaction.append(position, BLOCK_AIR, update)
        if broken_block.is_large:
            for break_target in broken_block.break_target:
                additional_position = position + break_target
                chunk, position_in_chunk = self._to_local(additional_position)
                update = partial(chunk.set_block, position_in_chunk, BLOCK_AIR)
                transaction.append(additional_position, BLOCK_AIR, update)
        return list(transaction.commit()), broken_block.to_item()

    def put_block(
            self,
            position: Vector3[int],
            face: Face,
            block: Block
    ) -> List[PlacedBlock]:
        """Put a block

        :param position: position to attach block
        :param face: face to attach block
        :param block: block to be attached
        :return: updated position and block
        """
        transaction = _Transaction()
        self._put_block(transaction, position, face, block)
        return list(transaction.commit())

    def _put_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            block: Block,
            on_ground: bool=False
    ) -> None:
        if on_ground:
            assert face is Face.TOP
        attached_block = CompositeBlock(block)
        if attached_block.has_layer:
            self._put_stackable_block(transaction, position, face, attached_block, on_ground)
        else:
            self._update_block(transaction, position, face, attached_block, on_ground)

    def _put_stackable_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            attached_block: CompositeBlock,
            on_ground: bool
    ) -> None:
        chunk, position_in_chunk = self._to_local(position)
        current_block = chunk.get_block(position_in_chunk)
        if attached_block.type == current_block.type:
            new_block = attached_block.stack_on(current_block, face)
            if new_block is not None:
                if new_block != current_block:
                    update = partial(chunk.set_block, position_in_chunk, new_block)
                    transaction.append(position, new_block, update)
                return
        chunk, position_in_chunk = self._to_local(position + face.direction)
        target_block = chunk.get_block(position_in_chunk)
        if attached_block.type == target_block.type:
            new_block = attached_block.stack_on(target_block, face.inverse)
            if new_block is not None:
                if new_block != target_block:
                    update = partial(chunk.set_block, position_in_chunk, new_block)
                    transaction.append(position + face.direction, new_block, update)
                return
        self._update_block(transaction, position, face, attached_block, on_ground)

    def _update_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            attached_block: CompositeBlock,
            on_ground: bool
    ) -> None:
        chunk, position_in_chunk = self._to_local(position)
        current_block = CompositeBlock(chunk.get_block(position_in_chunk))
        if not on_ground and current_block.is_switchable:
            position += current_block.switch_position
            chunk, position_in_chunk = self._to_local(position)
            switch_block = CompositeBlock(chunk.get_block(position_in_chunk))
            new_block = switch_block.switch()
            update = partial(chunk.set_block, position_in_chunk, new_block)
            transaction.append(position, new_block, update)
            return
        if not attached_block.can_be_attached_on(current_block.value, face):
            if not on_ground and attached_block.can_be_attached_on_ground:
                position += face.direction
                self._put_block(transaction, position - (0, 1, 0), Face.TOP, attached_block.value, on_ground=True)
            return
        position += face.direction
        self._link_blocks(position, attached_block)
        chunk, position_in_chunk = self._to_local(position)
        block = attached_block.value
        update = partial(chunk.set_block, position_in_chunk, block)
        transaction.append(position, block, update)

        if attached_block.is_large:
            for additional in attached_block.additional_blocks:
                additional_position = position + additional.position
                chunk, position_in_chunk = self._to_local(additional_position)
                current_block = chunk.get_block(position_in_chunk)
                if current_block.type is not BlockType.AIR:
                    transaction.clear()
                    return
                update = partial(chunk.set_block, position_in_chunk, additional.block)
                transaction.append(additional_position, additional.block, update)

    def _link_blocks(self, position: Vector3[int], attached_block: CompositeBlock) -> None:
        for link_target in attached_block.link_target:
            chunk, position_in_chunk = self._to_local(position + link_target)
            linking_block = chunk.get_block(position_in_chunk)
            attached_block.link_with(linking_block)

    def revise_position(self, position: Vector3[float]) -> Vector3[float]:
        height = self.get_height(position)
        return position.copy(y=height)
