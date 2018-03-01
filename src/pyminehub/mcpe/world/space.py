from functools import partial
from typing import Callable, Dict, Iterator, List, NamedTuple, Optional, Tuple

from pyminehub.mcpe.block import FunctionalBlock
from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.geometry import *
from pyminehub.mcpe.value import Item, Block, PlacedBlock
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


class _BlockCache:

    def __init__(
            self,
            position: Vector3[int],
            producer: Callable[[Vector3[int]], Tuple[Chunk, Vector3[int]]]
    ) -> None:
        chunk, position_in_chunk = producer(position)
        self._position = position
        self._chunk = chunk
        self._position_in_chunk = position_in_chunk
        self._block = chunk.get_block(position_in_chunk)

    @property
    def value(self) -> Block:
        return self._block

    def give_function(self) -> FunctionalBlock:
        return FunctionalBlock(self._block)

    def put(self, block: BlockType, transaction: _Transaction) -> None:
        update = partial(self._chunk.set_block, self._position_in_chunk, block)
        transaction.append(self._position, block, update)
        self._block = block


class Space:

    def __init__(self, generator: SpaceGenerator, store: DataStore) -> None:
        self._store = store
        self._generator = generator
        self._cache = {}  # type: Dict[ChunkPosition, Chunk]

    def init_space(self) -> None:
        self._generator.generate_space()

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

    def _get_cache(self, position: Vector3[int]) -> _BlockCache:
        return _BlockCache(position, self._to_local)

    def get_height(self, position: Vector3) -> int:
        """Get height by block position"""
        chunk, position_in_chunk = self._to_local(position)
        return chunk.get_height(position_in_chunk.x, position_in_chunk.z)

    def get_ceiling(self, position: Vector3) -> Optional[float]:
        """Get ceiling height by coordinate

        It search in the upward direction, when block can be passed through.
        It return height of position, when block can not be passed through.
        It return None, if there is not ceiling.
        """
        chunk, position_in_chunk = self._to_local(position)
        height = chunk.get_height(position_in_chunk.x, position_in_chunk.z)
        y = position_in_chunk.y
        while y < height:
            if not FunctionalBlock(chunk.get_block(position_in_chunk.copy(y=y))).can_pass:
                return y
            y += 1
        return None

    def get_floor(self, position: Vector3) -> float:
        """Get floor height by coordinate

        It search in the upward direction, when block can not be passed through.
        It search in the downward direction, when block can be passed through.
        """
        chunk, position_in_chunk = self._to_local(position)
        y = position_in_chunk.y
        while not FunctionalBlock(chunk.get_block(position_in_chunk.copy(y=y))).can_pass:
            y += 1
        while FunctionalBlock(chunk.get_block(position_in_chunk.copy(y=y))).can_pass:
            y -= 1
        return y + 1

    def break_block(self, position: Vector3[int]) -> Tuple[List[PlacedBlock], List[Item]]:
        """
        :param position: to break
        :return: updated position and block | spawned item list
        """
        block_cache = self._get_cache(position)
        broken_block = block_cache.give_function()
        if not broken_block.can_be_broken:
            return [], []
        transaction = _Transaction()
        for break_target in broken_block.break_target:
            self._get_cache(position + break_target).put(BLOCK_AIR, transaction)
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
        self._put_block(transaction, position, face, FunctionalBlock(block), on_ground=False)
        return list(transaction.commit())

    def _put_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            attached_block: FunctionalBlock,
            on_ground: bool
    ) -> None:
        if on_ground:
            assert face is Face.TOP
        if attached_block.has_layer:
            self._put_stackable_block(transaction, position, face, attached_block, on_ground)
        else:
            self._update_block(transaction, position, face, attached_block, on_ground)

    def _put_stackable_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            attached_block: FunctionalBlock,
            on_ground: bool
    ) -> None:
        current_block_cache = self._get_cache(position)
        if attached_block.type == current_block_cache.value.type:
            new_block = attached_block.stack_on(current_block_cache.value, face)
            if new_block is not None:
                if new_block != current_block_cache.value:
                    current_block_cache.put(new_block, transaction)
                return
        target_block_cache = self._get_cache(position + face.direction)
        if attached_block.type == target_block_cache.value.type:
            new_block = attached_block.stack_on(target_block_cache.value, face.inverse)
            if new_block is not None:
                if new_block != target_block_cache.value:
                    target_block_cache.put(new_block, transaction)
                return
        self._update_block(transaction, position, face, attached_block, on_ground)

    def _update_block(
            self,
            transaction: _Transaction,
            position: Vector3[int],
            face: Face,
            attached_block: FunctionalBlock,
            on_ground: bool
    ) -> None:
        current_block = self._get_cache(position).give_function()
        if not on_ground and current_block.is_switchable:
            switch_block_cache = self._get_cache(position + current_block.switch_position)
            new_block = switch_block_cache.give_function().switch()
            switch_block_cache.put(new_block, transaction)
            return
        if not attached_block.can_be_attached_on(current_block.value, face):
            if not on_ground and attached_block.can_be_attached_on_ground:
                position += face.direction
                self._put_block(transaction, position - (0, 1, 0), Face.TOP, attached_block, on_ground=True)
            return

        position += face.direction

        for additional in attached_block.get_additional_blocks(self._get_linked_blocks(position, attached_block)):
            current_block_cache = self._get_cache(position + additional.position)
            if not current_block_cache.give_function().can_be_overridden_by(additional.block):
                transaction.clear()
                return
            current_block_cache.put(additional.block, transaction)

    def _get_linked_blocks(self, position: Vector3[int], attached_block: FunctionalBlock) -> List[Block]:
        return list(self._get_cache(position + link_target).value for link_target in attached_block.link_target)

    def revise_position(self, oob: OrientedBoundingBox, on_ground: bool) -> Vector3[float]:
        if not on_ground and oob.bottom >= self.get_height(oob.origin):
            return oob.center_bottom
        while True:
            floor = self.get_floor(oob.origin.copy(y=oob.top))
            if oob.bottom < floor or on_ground:
                oob = oob.move(dy=floor - oob.bottom)
            ceiling = self.get_ceiling(oob.origin.copy(y=oob.top))
            if ceiling is None or oob.top <= ceiling:
                return oob.center_bottom
            oob = oob.move(dy=ceiling - oob.bottom)
