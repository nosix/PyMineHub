from typing import NamedTuple, Optional

from pyminehub.mcpe.const import ItemType, BlockType

__all__ = [
    'ItemSpec',
    'get_item_spec'
]


class ItemSpec(NamedTuple('ItemSpec', [
    ('block_type', Optional[BlockType]),
    ('max_quantity', int)
])):
    __slots__ = ()

    def to_block(self) -> Optional[BlockType]:
        return self.block_type


_item_specs = {
    ItemType.AIR: ItemSpec(None, 0),
    ItemType.DIRT: ItemSpec(BlockType.DIRT, 64),
    ItemType.STONE: ItemSpec(BlockType.STONE, 64)
}


def get_item_spec(item_type: ItemType) -> ItemSpec:
    return _item_specs[item_type]
