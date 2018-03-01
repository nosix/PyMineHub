from pyminehub.mcpe.block.spec import *
from pyminehub.mcpe.const import BlockType, ItemType

__all__ = [
    'block_specs'
]

block_specs = {
    BlockType.AIR: AirBlockSpec(),
    BlockType.BEDROCK: BlockSpec(None, can_be_broken=False),
    BlockType.GRASS: BlockSpec(ItemType.DIRT),
    BlockType.STONE_SLAB: SlabBlockSpec(ItemType.STONE_SLAB, BlockType.DOUBLE_STONE_SLAB),
    BlockType.WOODEN_SLAB: SlabBlockSpec(ItemType.WOODEN_SLAB, BlockType.DOUBLE_WOODEN_SLAB),
    BlockType.STONE_SLAB2: SlabBlockSpec(ItemType.STONE_SLAB2, BlockType.DOUBLE_STONE_SLAB2),
    BlockType.SNOW_LAYER: SnowLayerBlockSpec(),
    BlockType.LADDER: LadderBlockSpec(),
    BlockType.TRAPDOOR: TrapDoorBlockSpec(ItemType.TRAPDOOR),
    BlockType.IRON_TRAPDOOR: TrapDoorBlockSpec(ItemType.IRON_TRAPDOOR),
    BlockType.CARPET: CarpetBlockSpec(),
    BlockType.DOUBLE_PLANT: DoublePlantBlockSpec(ItemType.DOUBLE_PLANT),
    BlockType.CAKE_BLOCK: ToExtendUpwardBlockSpec(ItemType.CAKE),
    BlockType.BREWING_STAND_BLOCK: ToExtendUpwardBlockSpec(ItemType.BREWING_STAND),
    BlockType.FLOWER_POT_BLOCK: ToExtendUpwardBlockSpec(ItemType.FLOWER_POT, can_be_attached_on_ground=True),
    BlockType.END_ROD: EndRodBlockSpec(),
    BlockType.LEVER: ToggleBlockSpec(ItemType.LEVER),
    BlockType.WOODEN_BUTTON: ToggleBlockSpec(ItemType.WOODEN_BUTTON),
    BlockType.STONE_BUTTON: ToggleBlockSpec(ItemType.STONE_BUTTON),
    BlockType.TRIPWIRE_HOOK: TripwireHookBlockSpec(ItemType.TRIPWIRE_HOOK),
    BlockType.DAYLIGHT_DETECTOR: DaylightDetectorBlockSpec(ItemType.DAYLIGHT_DETECTOR),
    BlockType.DAYLIGHT_DETECTOR_INVERTED: DaylightDetectorBlockSpec(ItemType.DAYLIGHT_DETECTOR),
    BlockType.STANDING_BANNER: BlockSpec(ItemType.BANNER),
    BlockType.WALL_BANNER: BlockSpec(ItemType.BANNER),
    BlockType.STANDING_SIGN: BlockSpec(ItemType.SIGN),
    BlockType.WALL_SIGN: BlockSpec(ItemType.SIGN),
    BlockType.TORCH: TorchBlockSpec(ItemType.TORCH),
    BlockType.REDSTONE_TORCH: TorchBlockSpec(ItemType.REDSTONE_TORCH),
    BlockType.RAIL: RailBlockSpec(ItemType.RAIL),
    BlockType.GOLDEN_RAIL: RailBlockSpec(ItemType.GOLDEN_RAIL),
    BlockType.DETECTOR_RAIL: RailBlockSpec(ItemType.DETECTOR_RAIL),
    BlockType.ACTIVATOR_RAIL: RailBlockSpec(ItemType.ACTIVATOR_RAIL),
    BlockType.CHEST: ChestBlockSpec(ItemType.CHEST),
    BlockType.TRAPPED_CHEST: ChestBlockSpec(ItemType.TRAPPED_CHEST),
    BlockType.ENDER_CHEST: ChestBlockSpec(ItemType.ENDER_CHEST),
    BlockType.WEB: BlockSpec(ItemType.WEB, can_pass=True),
    BlockType.WATER: BlockSpec(None, can_pass=True, can_be_broken=False),
    BlockType.FLOWING_WATER: BlockSpec(None, can_pass=True, can_be_broken=False),
    BlockType.FLOWING_LAVA: BlockSpec(None, can_pass=True, can_be_broken=False),
}


_blocks = [
    # Construnction

    BlockType.PLANKS,

    BlockType.COBBLESTONE_WALL,

    BlockType.FENCE,
    BlockType.NETHER_BRICK_FENCE,

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

    BlockType.IRON_BARS,

    BlockType.GLASS,
    BlockType.STAINED_GLASS,
    BlockType.GLASS_PANE,
    BlockType.STAINED_GLASS_PANE,

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

    BlockType.DOUBLE_STONE_SLAB,
    BlockType.DOUBLE_WOODEN_SLAB,
    BlockType.DOUBLE_STONE_SLAB2,

    # Nature

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

    BlockType.MELON_BLOCK,
    BlockType.PUMPKIN,
    BlockType.LIT_PUMPKIN,

    BlockType.VINE,

    BlockType.SNOW,
    BlockType.ICE,
    BlockType.PACKED_ICE,

    BlockType.BROWN_MUSHROOM_BLOCK,
    BlockType.RED_MUSHROOM_BLOCK,

    BlockType.MOB_SPAWNER,

    BlockType.OBSIDIAN,
    BlockType.SOUL_SAND,
    BlockType.NETHERRACK,
    BlockType.MAGMA,
    BlockType.END_STONE,
    BlockType.SPONGE,

    # Items

    BlockType.REDSTONE_LAMP,
    BlockType.SEA_LANTERN,

    BlockType.GLOWSTONE,

    BlockType.BOOKSHELF,

    BlockType.END_PORTAL_FRAME,

    BlockType.GRASS_PATH,

    BlockType.TNT,
]

_fence_gate_blocks = [
    BlockType.FENCE_GATE,
    BlockType.SPRUCE_FENCE_GATE,
    BlockType.BIRCH_FENCE_GATE,
    BlockType.JUNGLE_FENCE_GATE,
    BlockType.ACACIA_FENCE_GATE,
    BlockType.DARK_OAK_FENCE_GATE,
]

_plant_blocks = [
    BlockType.SAPLING,
    BlockType.TALLGRASS,
    BlockType.YELLOW_FLOWER,
    BlockType.FLOWER,
    BlockType.LILY_PAD,
    BlockType.DEAD_BUSH,
    BlockType.BROWN_MUSHROOM,
    BlockType.RED_MUSHROOM,
]

_door_blocks = [
    (ItemType.WOODEN_DOOR, BlockType.WOODEN_DOOR_BLOCK),
    (ItemType.IRON_DOOR, BlockType.IRON_DOOR_BLOCK),
    (ItemType.SPRUCE_DOOR, BlockType.SPRUCE_DOOR_BLOCK),
    (ItemType.BIRCH_DOOR, BlockType.BIRCH_DOOR_BLOCK),
    (ItemType.JUNGLE_DOOR, BlockType.JUNGLE_DOOR_BLOCK),
    (ItemType.ACACIA_DOOR, BlockType.ACACIA_DOOR_BLOCK),
    (ItemType.DARK_OAK_DOOR, BlockType.DARK_OAK_DOOR_BLOCK),
]

_tool_blocks = [
    BlockType.CRAFTING_TABLE,
    BlockType.FURNACE,
    BlockType.ANVIL,
    BlockType.ENCHANTING_TABLE,
    BlockType.NOTEBLOCK,
    BlockType.STONECUTTER,
]

_pressure_plate_blocks = [
    BlockType.WOODEN_PRESSURE_PLATE,
    BlockType.STONE_PRESSURE_PLATE,
    BlockType.LIGHT_WEIGHTED_PRESSURE_PLATE,
    BlockType.HEAVY_WEIGHTED_PRESSURE_PLATE,
]


for _block_type in _blocks:
    block_specs[_block_type] = BlockSpec(ItemType(_block_type.value))

for _block_type in _fence_gate_blocks:
    block_specs[_block_type] = FenceGateBlockSpec(ItemType(_block_type.value))

for _block_type in _plant_blocks:
    block_specs[_block_type] = ToExtendUpwardBlockSpec(ItemType(_block_type.value), can_pass=True)

for _item_type, _block_type in _door_blocks:
    block_specs[_block_type] = DoorBlockSpec(_item_type)

for _block_type in _tool_blocks:
    block_specs[_block_type] = ToExtendUpwardBlockSpec(ItemType(_block_type.value))

for _block_type in _pressure_plate_blocks:
    block_specs[_block_type] = ToExtendUpwardBlockSpec(ItemType(_block_type.value))
