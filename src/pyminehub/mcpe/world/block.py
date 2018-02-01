from typing import Dict, List, Optional

from pyminehub.mcpe.const import BlockType, ItemType
from pyminehub.mcpe.geometry import Face
from pyminehub.mcpe.value import Item, Block

__all__ = [
    'BlockSpec',
    'BlockModel'
]


class BlockSpec:

    def __init__(self, item_type: Optional[ItemType], max_layer_num: int=1) -> None:
        self._item_type = item_type
        self._max_layer_num = max_layer_num

    @property
    def item_type(self) -> Optional[ItemType]:
        return self._item_type

    @property
    def max_layer_num(self) -> int:
        return self._max_layer_num

    def to_item(self, block_data: int) -> List[Item]:
        return [Item.create(self.item_type, 1, block_data)] if self.item_type is not None else []

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()


class SlabBlockSpec(BlockSpec):

    _SLAB_TYPE_MASK = 0b111
    _IS_UPPER_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType], layered_block_type: Dict[int, Block]) -> None:
        super().__init__(item_type, 2)
        self._layered_block_type = layered_block_type

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        """
        >>> spec = SlabBlockSpec(None, {0: Block.create(BlockType.PLANKS, 0)})
        >>> block_type = BlockType.WOODEN_SLAB
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8), Face.TOP)
        Block(type=<BlockType.PLANKS: 5>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 8), Block.create(block_type, 0), Face.BOTTOM)
        Block(type=<BlockType.PLANKS: 5>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 8), Block.create(block_type, 0), Face.TOP)
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8), Face.BOTTOM)
        >>> spec.stack_layer(Block.create(block_type, 0, neighbors=True), Block.create(block_type, 8), Face.TOP)
        Block(type=<BlockType.PLANKS: 5>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8, neighbors=True), Face.TOP)
        Block(type=<BlockType.PLANKS: 5>, aux_value=16)
        >>> spec.stack_layer(\\
        ...     Block.create(block_type, 0, neighbors=True), Block.create(block_type, 8, neighbors=False), Face.TOP)
        Block(type=<BlockType.PLANKS: 5>, aux_value=0)
        """
        slab_type = stacked_block.data & self._SLAB_TYPE_MASK
        if slab_type != base_block.data & self._SLAB_TYPE_MASK:
            return base_block
        is_upper = stacked_block.data & self._IS_UPPER_MASK
        if is_upper != base_block.data & self._IS_UPPER_MASK:
            if (face is Face.BOTTOM and is_upper) or (face is Face.TOP and not is_upper):
                return None
            return self._layered_block_type[slab_type].copy(**stacked_block.flags)
        return None


_block_specs = {
    BlockType.AIR: BlockSpec(None),
    BlockType.GRASS: BlockSpec(ItemType.DIRT),
    BlockType.STONE_SLAB: SlabBlockSpec(ItemType.STONE_SLAB, {
        0: Block.create(BlockType.DOUBLE_STONE_SLAB, 0),
        1: Block.create(BlockType.DOUBLE_STONE_SLAB, 1),
        3: Block.create(BlockType.DOUBLE_STONE_SLAB, 3),
        4: Block.create(BlockType.DOUBLE_STONE_SLAB, 4),
        5: Block.create(BlockType.DOUBLE_STONE_SLAB, 5),
        7: Block.create(BlockType.DOUBLE_STONE_SLAB, 7),
    }),
    BlockType.WOODEN_SLAB: SlabBlockSpec(ItemType.WOODEN_SLAB, {
        0: Block.create(BlockType.PLANKS, 0),
        1: Block.create(BlockType.PLANKS, 1),
        2: Block.create(BlockType.PLANKS, 2),
        3: Block.create(BlockType.PLANKS, 3),
        4: Block.create(BlockType.PLANKS, 4),
        5: Block.create(BlockType.PLANKS, 5),
    }),
    BlockType.STONE_SLAB2: BlockSpec(ItemType.STONE_SLAB2, 2),
}


_blocks = [
    BlockType.PLANKS,

    BlockType.COBBLESTONE_WALL,

    BlockType.FENCE,
    BlockType.NETHER_BRICK_FENCE,

    BlockType.FENCE_GATE,
    BlockType.SPRUCE_FENCE_GATE,
    BlockType.BIRCH_FENCE_GATE,
    BlockType.JUNGLE_FENCE_GATE,
    BlockType.ACACIA_FENCE_GATE,
    BlockType.DARK_OAK_FENCE_GATE,

    BlockType.STONE_STAIRS,
    BlockType.OAK_STAIRS,
    BlockType.SPRUCE_STAIRS,
    BlockType.BIRCH_STAIRS,
    BlockType.JUNGLE_STAIRS,
    BlockType.ACACIA_STAIRS,
    BlockType.DARK_OAK_STAIRS,
    BlockType.BRICK_STAIRS,
    BlockType.STONE_BRICK_STAIRS,
    BlockType.NETHER_BRICK_STAIRS,
    BlockType.SANDSTONE_STAIRS,
    BlockType.RED_SANDSTONE_STAIRS,
    BlockType.QUARTZ_STAIRS,
    BlockType.PURPUR_STAIRS,

    BlockType.TRAPDOOR,
    BlockType.IRON_TRAPDOOR,

    BlockType.IRON_BARS,

    BlockType.GLASS,
    BlockType.STAINED_GLASS,
    BlockType.GLASS_PANE,
    BlockType.STAINED_GLASS_PANE,

    BlockType.LADDER,

    BlockType.BRICK_BLOCK,
    BlockType.STONE_BRICK,
    BlockType.END_BRICK,
    BlockType.PRISMARINE,
    BlockType.NETHER_BRICK_BLOCK,
    BlockType.RED_NETHER_BRICK,
    BlockType.COBBLESTONE,
    BlockType.MOSSY_COBBLESTONE,

    BlockType.SANDSTONE,
    BlockType.RED_SANDSTONE,
    BlockType.COAL_BLOCK,
    BlockType.REDSTONE_BLOCK,
    BlockType.GOLD_BLOCK,
    BlockType.IRON_BLOCK,
    BlockType.EMERALD_BLOCK,
    BlockType.DIAMOND_BLOCK,
    BlockType.LAPIS_BLOCK,
    BlockType.QUARTZ_BLOCK,
    BlockType.HAY_BLOCK,
    BlockType.BONE_BLOCK,
    BlockType.NETHER_WART_BLOCK,
    BlockType.WOOL,

    BlockType.CARPET,

    BlockType.CONCRETE_POWDER,
    BlockType.CONCRETE,
    BlockType.CLAY,
    BlockType.HARDENED_CLAY,
    BlockType.STAINED_HARDENED_CLAY,
    BlockType.WHITE_GLAZED_TERRACOTTA,
    BlockType.SILVER_GLAZED_TERRACOTTA,
    BlockType.GRAY_GLAZED_TERRACOTTA,
    BlockType.BLACK_GLAZED_TERRACOTTA,
    BlockType.BROWN_GLAZED_TERRACOTTA,
    BlockType.RED_GLAZED_TERRACOTTA,
    BlockType.ORANGE_GLAZED_TERRACOTTA,
    BlockType.YELLOW_GLAZED_TERRACOTTA,
    BlockType.LIME_GLAZED_TERRACOTTA,
    BlockType.GREEN_GLAZED_TERRACOTTA,
    BlockType.CYAN_GLAZED_TERRACOTTA,
    BlockType.LIGHT_BLUE_GLAZED_TERRACOTTA,
    BlockType.BLUE_GLAZED_TERRACOTTA,
    BlockType.PURPLE_GLAZED_TERRACOTTA,
    BlockType.MAGENTA_GLAZED_TERRACOTTA,
    BlockType.PINK_GLAZED_TERRACOTTA,
    BlockType.PURPUR_BLOCK,
    BlockType.DIRT,
    BlockType.PODZOL,
    BlockType.MYCELIUM,
    BlockType.STONE,
    BlockType.IRON_ORE,
    BlockType.GOLD_ORE,
    BlockType.DIAMOND_ORE,
    BlockType.LAPIS_ORE,
    BlockType.REDSTONE_ORE,
    BlockType.COAL_ORE,
    BlockType.EMERALD_ORE,
    BlockType.QUARTZ_ORE,
    BlockType.GRAVEL,
    BlockType.SAND,
    BlockType.CACTUS,
    BlockType.LOG,
    BlockType.LOG2,
    BlockType.LEAVES,
    BlockType.LEAVES2,

    BlockType.SAPLING,

    BlockType.MELON_BLOCK,
    BlockType.PUMPKIN,
    BlockType.LIT_PUMPKIN,

    BlockType.TALLGRASS,
    BlockType.DOUBLE_PLANT,
    BlockType.YELLOW_FLOWER,
    BlockType.FLOWER,

    BlockType.VINE,

    BlockType.SNOW,
    BlockType.ICE,
    BlockType.PACKED_ICE,
    BlockType.SNOW_LAYER,

    BlockType.BROWN_MUSHROOM_BLOCK,
    BlockType.RED_MUSHROOM_BLOCK,

    BlockType.MOB_SPAWNER,

    BlockType.OBSIDIAN,
    BlockType.BEDROCK,
    BlockType.SOUL_SAND,
    BlockType.NETHERRACK,
    BlockType.MAGMA,
    BlockType.END_STONE,
    BlockType.SPONGE,

    BlockType.WEB,

    BlockType.TORCH,
    BlockType.REDSTONE_TORCH,
    BlockType.REDSTONE_LAMP,
    BlockType.SEA_LANTERN,

    BlockType.GLOWSTONE,

    BlockType.CRAFTING_TABLE,
    BlockType.FURNACE,

    BlockType.ANVIL,

    BlockType.STONECUTTER,
    BlockType.CHEST,
    BlockType.TRAPPED_CHEST,
    BlockType.ENDER_CHEST,
    BlockType.BOOKSHELF,
    BlockType.ENCHANTING_TABLE,
    BlockType.NOTEBLOCK,

    BlockType.DAYLIGHT_DETECTOR,
    BlockType.END_PORTAL_FRAME,

    BlockType.GRASS_PATH,

    BlockType.RAIL,
    BlockType.GOLDEN_RAIL,
    BlockType.DETECTOR_RAIL,
    BlockType.ACTIVATOR_RAIL,
    BlockType.LEVER,
    BlockType.WOODEN_BUTTON,
    BlockType.STONE_BUTTON,
    BlockType.TRIPWIRE_HOOK,
    BlockType.WOODEN_PRESSURE_PLATE,
    BlockType.STONE_PRESSURE_PLATE,
    BlockType.LIGHT_WEIGHTED_PRESSURE_PLATE,
    BlockType.HEAVY_WEIGHTED_PRESSURE_PLATE,

    BlockType.TNT,

    BlockType.DOUBLE_STONE_SLAB,
]


for _block_type in _blocks:
    _block_specs[_block_type] = BlockSpec(ItemType(_block_type.value))


class BlockModel:

    def __init__(self, block: Block) -> None:
        self._block = block
        self._block_spec = _block_specs[block.type]

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
        return self._block_spec.max_layer_num > 1

    def to_item(self) -> List[Item]:
        return self._block_spec.to_item(self._block.data)

    def stack_layer(self, stacked_block: 'BlockModel', face: Face) -> Optional[Block]:
        return self._block_spec.stack_layer(self._block, stacked_block._block, face)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
