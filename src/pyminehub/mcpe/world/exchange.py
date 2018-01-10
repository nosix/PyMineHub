from typing import NamedTuple as _NamedTuple, List, Optional

from pyminehub.mcpe.const import BlockType, ItemType
from pyminehub.mcpe.value import Item


class BlockSpec(_NamedTuple('BlockSpec', [
    ('item', Item)  # TODO support many items
])):
    def to_item(self) -> List[Item]:
        return [self.item]


_block_specs = {
    BlockType.GRASS: BlockSpec(Item.create(ItemType.DIRT, 1)),
    BlockType.STONE: BlockSpec(Item.create(ItemType.STONE, 1))
}


def block_to_item(block_type: BlockType) -> List[Item]:
    return _block_specs[block_type].to_item()


def item_to_block(item: Item) -> Optional[BlockType]:
    try:
        return BlockType[item.type.name]
    except KeyError:
        return None
