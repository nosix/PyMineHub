from typing import Dict, Optional

from pyminehub.mcpe.const import ItemType, BlockType
from pyminehub.mcpe.geometry import Face
from pyminehub.mcpe.value import Block

__all__ = [
    'ItemSpec',
    'get_item_spec'
]


class ItemSpec:

    def __init__(self, block_type: Optional[BlockType], max_quantity: int) -> None:
        self._block_type = block_type
        self._max_quantity = max_quantity

    @property
    def block_type(self) -> Optional[BlockType]:
        return self._block_type

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    def to_block(self, item_data: int, attached_face: Face, horizontal_player_face: Face, **kwargs) -> Optional[Block]:
        if self.block_type is None:
            return None
        block_data = self.to_block_data(item_data, attached_face, horizontal_player_face, kwargs)
        return Block.create(self.block_type, block_data, **kwargs)

    def to_block_data(self, item_data: int, attached_face: Face, horizontal_player_face: Face, kwargs: Dict) -> int:
        raise NotImplementedError()


class DefaultItemSpec(ItemSpec):

    def to_block_data(self, item_data: int, attached_face: Face, horizontal_player_face: Face, kwargs: Dict) -> int:
        return item_data


class DirectivityItemSpec(ItemSpec):

    def to_block_data(self, item_data: int, attached_face: Face, horizontal_player_face: Face, kwargs: Dict) -> int:
        return attached_face.value if attached_face.direction.y == 0 else horizontal_player_face.inverse.value


_item_specs = {
    ItemType.AIR: DefaultItemSpec(None, 0),
}

_block_items = [
    ItemType.PLANKS,

    ItemType.COBBLESTONE_WALL,

    ItemType.FENCE,
    ItemType.NETHER_BRICK_FENCE,

    ItemType.FENCE_GATE,
    ItemType.SPRUCE_FENCE_GATE,
    ItemType.BIRCH_FENCE_GATE,
    ItemType.JUNGLE_FENCE_GATE,
    ItemType.ACACIA_FENCE_GATE,
    ItemType.DARK_OAK_FENCE_GATE,

    ItemType.STONE_STAIRS,
    ItemType.OAK_STAIRS,
    ItemType.SPRUCE_STAIRS,
    ItemType.BIRCH_STAIRS,
    ItemType.JUNGLE_STAIRS,
    ItemType.ACACIA_STAIRS,
    ItemType.DARK_OAK_STAIRS,
    ItemType.BRICK_STAIRS,
    ItemType.STONE_BRICK_STAIRS,
    ItemType.NETHER_BRICK_STAIRS,
    ItemType.SANDSTONE_STAIRS,
    ItemType.RED_SANDSTONE_STAIRS,
    ItemType.QUARTZ_STAIRS,
    ItemType.PURPUR_STAIRS,

    ItemType.TRAPDOOR,
    ItemType.IRON_TRAPDOOR,

    ItemType.IRON_BARS,

    ItemType.GLASS,
    ItemType.STAINED_GLASS,
    ItemType.GLASS_PANE,
    ItemType.STAINED_GLASS_PANE,

    ItemType.LADDER,

    ItemType.STONE_SLAB,
    ItemType.WOODEN_SLAB,
    ItemType.STONE_SLAB2,

    ItemType.BRICK_BLOCK,
    ItemType.STONE_BRICK,
    ItemType.END_BRICK,
    ItemType.PRISMARINE,
    ItemType.NETHER_BRICK_BLOCK,
    ItemType.RED_NETHER_BRICK,
    ItemType.COBBLESTONE,
    ItemType.MOSSY_COBBLESTONE,

    ItemType.SANDSTONE,
    ItemType.RED_SANDSTONE,
    ItemType.COAL_BLOCK,
    ItemType.REDSTONE_BLOCK,
    ItemType.GOLD_BLOCK,
    ItemType.IRON_BLOCK,
    ItemType.EMERALD_BLOCK,
    ItemType.DIAMOND_BLOCK,
    ItemType.LAPIS_BLOCK,
    ItemType.QUARTZ_BLOCK,
    ItemType.HAY_BLOCK,
    ItemType.BONE_BLOCK,
    ItemType.NETHER_WART_BLOCK,
    ItemType.WOOL,

    ItemType.CARPET,

    ItemType.CONCRETE_POWDER,
    ItemType.CONCRETE,
    ItemType.CLAY,
    ItemType.HARDENED_CLAY,
    ItemType.STAINED_HARDENED_CLAY,
    ItemType.PURPUR_BLOCK,
    ItemType.DIRT,
    ItemType.GRASS,
    ItemType.PODZOL,
    ItemType.MYCELIUM,
    ItemType.STONE,
    ItemType.IRON_ORE,
    ItemType.GOLD_ORE,
    ItemType.DIAMOND_ORE,
    ItemType.LAPIS_ORE,
    ItemType.REDSTONE_ORE,
    ItemType.COAL_ORE,
    ItemType.EMERALD_ORE,
    ItemType.QUARTZ_ORE,
    ItemType.GRAVEL,
    ItemType.SAND,
    ItemType.CACTUS,
    ItemType.LOG,
    ItemType.LOG2,
    ItemType.LEAVES,
    ItemType.LEAVES2,

    ItemType.SAPLING,

    ItemType.MELON_BLOCK,
    ItemType.PUMPKIN,
    ItemType.LIT_PUMPKIN,

    ItemType.TALLGRASS,
    ItemType.DOUBLE_PLANT,
    ItemType.YELLOW_FLOWER,
    ItemType.FLOWER,

    ItemType.VINE,

    ItemType.SNOW,
    ItemType.ICE,
    ItemType.PACKED_ICE,
    ItemType.SNOW_LAYER,

    ItemType.BROWN_MUSHROOM_BLOCK,
    ItemType.RED_MUSHROOM_BLOCK,

    ItemType.MOB_SPAWNER,

    ItemType.OBSIDIAN,
    ItemType.BEDROCK,
    ItemType.SOUL_SAND,
    ItemType.NETHERRACK,
    ItemType.MAGMA,
    ItemType.END_STONE,
    ItemType.SPONGE,

    ItemType.WEB,

    ItemType.TORCH,
    ItemType.REDSTONE_TORCH,
    ItemType.REDSTONE_LAMP,
    ItemType.SEA_LANTERN,

    ItemType.GLOWSTONE,

    ItemType.CRAFTING_TABLE,
    ItemType.FURNACE,

    ItemType.ANVIL,

    ItemType.STONECUTTER,
    ItemType.CHEST,
    ItemType.TRAPPED_CHEST,
    ItemType.ENDER_CHEST,
    ItemType.BOOKSHELF,
    ItemType.ENCHANTING_TABLE,
    ItemType.NOTEBLOCK,

    ItemType.DAYLIGHT_DETECTOR,
    ItemType.END_PORTAL_FRAME,

    ItemType.GRASS_PATH,

    ItemType.RAIL,
    ItemType.GOLDEN_RAIL,
    ItemType.DETECTOR_RAIL,
    ItemType.ACTIVATOR_RAIL,
    ItemType.LEVER,
    ItemType.WOODEN_BUTTON,
    ItemType.STONE_BUTTON,
    ItemType.TRIPWIRE_HOOK,
    ItemType.WOODEN_PRESSURE_PLATE,
    ItemType.STONE_PRESSURE_PLATE,
    ItemType.LIGHT_WEIGHTED_PRESSURE_PLATE,
    ItemType.HEAVY_WEIGHTED_PRESSURE_PLATE,

    ItemType.TNT,
]

_directivity_block_items = [
    ItemType.WHITE_GLAZED_TERRACOTTA,
    ItemType.SILVER_GLAZED_TERRACOTTA,
    ItemType.GRAY_GLAZED_TERRACOTTA,
    ItemType.BLACK_GLAZED_TERRACOTTA,
    ItemType.BROWN_GLAZED_TERRACOTTA,
    ItemType.RED_GLAZED_TERRACOTTA,
    ItemType.ORANGE_GLAZED_TERRACOTTA,
    ItemType.YELLOW_GLAZED_TERRACOTTA,
    ItemType.LIME_GLAZED_TERRACOTTA,
    ItemType.GREEN_GLAZED_TERRACOTTA,
    ItemType.CYAN_GLAZED_TERRACOTTA,
    ItemType.LIGHT_BLUE_GLAZED_TERRACOTTA,
    ItemType.BLUE_GLAZED_TERRACOTTA,
    ItemType.PURPLE_GLAZED_TERRACOTTA,
    ItemType.MAGENTA_GLAZED_TERRACOTTA,
    ItemType.PINK_GLAZED_TERRACOTTA,
]


for _item_type in _block_items:
    _item_specs[_item_type] = DefaultItemSpec(BlockType(_item_type.value), 64)

for _item_type in _directivity_block_items:
    _item_specs[_item_type] = DirectivityItemSpec(BlockType(_item_type.value), 64)


def get_item_spec(item_type: ItemType) -> ItemSpec:
    return _item_specs[item_type]
