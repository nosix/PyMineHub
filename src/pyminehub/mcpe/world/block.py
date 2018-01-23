from typing import List, NamedTuple, Optional

from pyminehub.mcpe.const import BlockType, ItemType
from pyminehub.mcpe.value import Item

__all__ = [
    'BlockSpec',
    'get_block_spec'
]


class BlockSpec(NamedTuple('BlockSpec', [
    ('item', Optional[Item])  # TODO support many items
])):
    __slots__ = ()

    def to_item(self) -> List[Item]:
        return [self.item] if self.item is not None else []


_block_specs = {
    BlockType.GRASS: BlockSpec(Item.create(ItemType.DIRT, 1)),
    BlockType.DIRT: BlockSpec(Item.create(ItemType.DIRT, 1)),
    BlockType.STONE: BlockSpec(Item.create(ItemType.STONE, 1))
}


def get_block_spec(block_type: BlockType) -> BlockSpec:
    return _block_specs[block_type]
