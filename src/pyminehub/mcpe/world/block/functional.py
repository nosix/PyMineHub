from typing import List, Optional, Sequence, Tuple

from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.value import Item, Block, PlacedBlock
from pyminehub.mcpe.world.block.catalog import block_specs

__all__ = [
    'FunctionalBlock'
]


class FunctionalBlock:
    """Functional block joins block value and block specification"""

    def __init__(self, block: Block) -> None:
        self._block = block
        self._block_spec = block_specs[block.type]

    def __str__(self) -> str:
        return str(self._block)

    @property
    def type(self) -> BlockType:
        return self._block.type

    @property
    def value(self) -> Block:
        return self._block

    @property
    def has_layer(self) -> bool:
        return self._block_spec.has_layer

    @property
    def can_be_broken(self) -> bool:
        return self._block_spec.can_be_broken

    @property
    def can_be_attached_on_ground(self) -> bool:
        return self._block_spec.can_be_attached_on_ground

    @property
    def is_switchable(self) -> bool:
        return self._block_spec.is_switchable

    @property
    def switch_position(self) -> Vector3[int]:
        return self._block_spec.get_switch_position(self._block)

    @property
    def link_target(self) -> Tuple[Vector3[int], ...]:
        return self._block_spec.get_link_target(self._block)

    @property
    def break_target(self) -> Tuple[Vector3[int], ...]:
        return self._block_spec.get_break_target(self._block)

    def to_item(self) -> List[Item]:
        return self._block_spec.to_item(self._block.data)

    def stack_on(self, base_block: Block, face: Face) -> Optional[Block]:
        return self._block_spec.stack_layer(base_block, self._block, face)

    def switch(self) -> Block:
        return self._block_spec.switch(self._block)

    def can_be_attached_on(self, base_block: Block, face: Face) -> bool:
        if face.inverse not in self._block_spec.male_connector(self._block):
            return False
        base_block_spec = block_specs[base_block.type]
        if face not in base_block_spec.female_connector(base_block):
            return False
        return self._block_spec.can_be_attached_on(base_block)

    def get_additional_blocks(self, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        return self._block_spec.get_additional_blocks(self._block, linked_blocks)

    def can_be_overridden_by(self, block: Block) -> bool:
        return self._block_spec.can_be_overridden_by(block)
