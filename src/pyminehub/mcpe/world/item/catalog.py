from pyminehub.mcpe.const import ItemType, BlockType
from pyminehub.mcpe.world.item.spec import *

__all__ = [
    'get_item_spec'
]

_item_specs = {
    ItemType.AIR: DefaultItemSpec(None, 0),
    ItemType.HAY_BLOCK: DirectionalItemSpec(BlockType.HAY_BLOCK, 64, (0,)),
    ItemType.BONE_BLOCK: DirectionalItemSpec(BlockType.BONE_BLOCK, 64, (0,)),
    ItemType.QUARTZ_BLOCK: DirectionalItemSpec(BlockType.QUARTZ_BLOCK, 64, (1, 2)),
    ItemType.PURPUR_BLOCK: DirectionalItemSpec(BlockType.PURPUR_BLOCK, 64, (2,)),
    ItemType.LOG: DirectionalItemSpec(BlockType.LOG, 64, (0, 1, 2, 3)),
    ItemType.LOG2: DirectionalItemSpec(BlockType.LOG2, 64, (0, 1)),
    ItemType.PUMPKIN: PumpkinSpec(BlockType.PUMPKIN, 64),
    ItemType.LIT_PUMPKIN: PumpkinSpec(BlockType.LIT_PUMPKIN, 64),
    ItemType.STONE_SLAB: SlabItemSpec(BlockType.STONE_SLAB, 64),
    ItemType.WOODEN_SLAB: SlabItemSpec(BlockType.WOODEN_SLAB, 64),
    ItemType.STONE_SLAB2: SlabItemSpec(BlockType.STONE_SLAB2, 64),
    ItemType.LADDER: LadderItemSpec(BlockType.LADDER, 64),
    ItemType.TRAPDOOR: TrapDoorItemSpec(BlockType.TRAPDOOR, 64),
    ItemType.IRON_TRAPDOOR: TrapDoorItemSpec(BlockType.IRON_TRAPDOOR, 64),
    ItemType.CAKE: DefaultItemSpec(BlockType.CAKE_BLOCK, 64),
    ItemType.BUCKET: BucketItemSpec(),
    ItemType.FURNACE: FurnaceItemSpec(BlockType.FURNACE, 64),
    ItemType.BREWING_STAND: DefaultItemSpec(BlockType.BREWING_STAND_BLOCK, 64),
    ItemType.ANVIL: AnvilItemSpec(BlockType.ANVIL, 64),
    ItemType.FLOWER_POT: DefaultItemSpec(BlockType.FLOWER_POT_BLOCK, 64),
    ItemType.END_ROD: EndRodItemSpec(BlockType.END_ROD, 64),
    ItemType.LEVER: LeverItemSpec(BlockType.LEVER, 64),
    ItemType.WOODEN_BUTTON: ButtonItemSpec(BlockType.WOODEN_BUTTON, 64),
    ItemType.STONE_BUTTON: ButtonItemSpec(BlockType.STONE_BUTTON, 64),
    ItemType.TRIPWIRE_HOOK: TripwireHookItemSpec(),
    ItemType.BANNER: StandingOrWallItemSpec(BlockType.STANDING_BANNER, BlockType.WALL_BANNER),
    ItemType.SIGN: StandingOrWallItemSpec(BlockType.STANDING_SIGN, BlockType.WALL_SIGN),
    ItemType.TORCH: TorchItemSpec(BlockType.TORCH, 64),
    ItemType.REDSTONE_TORCH: TorchItemSpec(BlockType.REDSTONE_TORCH, 64),
    ItemType.CHEST: ChestItemSpec(BlockType.CHEST, 64),
    ItemType.TRAPPED_CHEST: ChestItemSpec(BlockType.TRAPPED_CHEST, 64),
    ItemType.ENDER_CHEST: ChestItemSpec(BlockType.ENDER_CHEST, 64),
}

_block_items = [
    # Construction

    ItemType.PLANKS,

    ItemType.COBBLESTONE_WALL,

    ItemType.FENCE,
    ItemType.NETHER_BRICK_FENCE,

    ItemType.IRON_BARS,

    ItemType.GLASS,
    ItemType.STAINED_GLASS,
    ItemType.GLASS_PANE,
    ItemType.STAINED_GLASS_PANE,

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
    ItemType.NETHER_WART_BLOCK,

    ItemType.WOOL,

    ItemType.CARPET,

    ItemType.CONCRETE_POWDER,
    ItemType.CONCRETE,

    ItemType.CLAY,
    ItemType.HARDENED_CLAY,
    ItemType.STAINED_HARDENED_CLAY,

    # Nature

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

    ItemType.LEAVES,
    ItemType.LEAVES2,

    ItemType.SAPLING,

    ItemType.MELON_BLOCK,

    ItemType.TALLGRASS,
    ItemType.DOUBLE_PLANT,
    ItemType.YELLOW_FLOWER,
    ItemType.FLOWER,

    ItemType.VINE,
    ItemType.LILY_PAD,
    ItemType.DEAD_BUSH,

    ItemType.SNOW,
    ItemType.ICE,
    ItemType.PACKED_ICE,
    ItemType.SNOW_LAYER,

    ItemType.BROWN_MUSHROOM,
    ItemType.RED_MUSHROOM,
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

    ItemType.REDSTONE_LAMP,
    ItemType.SEA_LANTERN,

    ItemType.GLOWSTONE,

    ItemType.CRAFTING_TABLE,

    ItemType.STONECUTTER,
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
    ItemType.WOODEN_PRESSURE_PLATE,
    ItemType.STONE_PRESSURE_PLATE,
    ItemType.LIGHT_WEIGHTED_PRESSURE_PLATE,
    ItemType.HEAVY_WEIGHTED_PRESSURE_PLATE,

    ItemType.TNT,
]

_stairs_block_items = [
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
]

_terracotta_block_items = [
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

_fence_gate_block_items = [
    ItemType.FENCE_GATE,
    ItemType.SPRUCE_FENCE_GATE,
    ItemType.BIRCH_FENCE_GATE,
    ItemType.JUNGLE_FENCE_GATE,
    ItemType.ACACIA_FENCE_GATE,
    ItemType.DARK_OAK_FENCE_GATE,
]

_door_items = [
    (ItemType.WOODEN_DOOR, BlockType.WOODEN_DOOR_BLOCK),
    (ItemType.IRON_DOOR, BlockType.IRON_DOOR_BLOCK),
    (ItemType.SPRUCE_DOOR, BlockType.SPRUCE_DOOR_BLOCK),
    (ItemType.BIRCH_DOOR, BlockType.BIRCH_DOOR_BLOCK),
    (ItemType.JUNGLE_DOOR, BlockType.JUNGLE_DOOR_BLOCK),
    (ItemType.ACACIA_DOOR, BlockType.ACACIA_DOOR_BLOCK),
    (ItemType.DARK_OAK_DOOR, BlockType.DARK_OAK_DOOR_BLOCK),
]


for _item_type in _block_items:
    _item_specs[_item_type] = DefaultItemSpec(BlockType(_item_type.value), 64)

for _item_type in _stairs_block_items:
    _item_specs[_item_type] = StairItemSpec(BlockType(_item_type.value), 64)

for _item_type in _terracotta_block_items:
    _item_specs[_item_type] = TerracottaItemSpec(BlockType(_item_type.value), 64)

for _item_type in _fence_gate_block_items:
    _item_specs[_item_type] = FenceGateItemSpec(BlockType(_item_type.value), 64)

for _item_type, _block_type in _door_items:
    _item_specs[_item_type] = DoorItemSpec(_block_type, 64)


def get_item_spec(item_type: ItemType) -> ItemSpec:
    return _item_specs[item_type]
