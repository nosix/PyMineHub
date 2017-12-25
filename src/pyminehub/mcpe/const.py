from enum import Enum


class PlayStatus(Enum):
    LOGIN_SUCCESS = 0
    LOGIN_FAILED_CLIENT = 1
    LOGIN_FAILED_SERVER = 2
    PLAYER_SPAWN = 3
    LOGIN_FAILED_INVALID_TENANT = 4
    LOGIN_FAILED_VANILLA_EDU = 5
    LOGIN_FAILED_EDU_VANILLA = 6


class ResourcePackStatus(Enum):
    REFUSED = 1
    SEND_PACKS = 2
    HAVE_ALL_PACKS = 3
    COMPLETED = 4


class Dimension(Enum):
    OVERWORLD = 0
    NETHER = 1
    THE_END = 2

    
class Generator(Enum):
    OLD = 0
    INFINITE = 1
    FLAT = 2


class GameMode(Enum):
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2


class Difficulty(Enum):
    PEACEFUL = 0
    EASY = 1
    NORMAL = 2
    HARD = 3

    
class GameRuleType(Enum):
    BOOL = 1
    INT = 2
    FLOAT = 3


class PlayerPermission(Enum):
    CUSTOM = 3
    OPERATOR = 2
    MEMBER = 1
    VISITOR = 0


class CommandPermission(Enum):
    NORMAL = 0
    OPERATOR = 1
    HOST = 2
    AUTOMATION = 3
    ADMIN = 4


class AdventureSettingFlags1(Enum):
    WORLD_IMMUTABLE = 0x01
    NO_PVP = 0x02
    AUTO_JUMP = 0x20
    ALLOW_FLIGHT = 0x40
    NO_CLIP = 0x80
    WORLD_BUILDER = 0x100
    FLYING = 0x200
    MUTED = 0x400


class AdventureSettingFlags2(Enum):
    BUILD_AND_MINE = 0x01
    DOORS_AND_SWITCHES = 0x02
    OPEN_CONTAINERS = 0x04
    ATTACK_PLAYERS = 0x08
    ATTACK_MOBS = 0x10
    OPERATOR = 0x20
    TELEPORT = 0x80


class MetaDataType(Enum):
    BYTE = 0
    SHORT = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    SLOT = 5
    INT_VECTOR3 = 6
    LONG = 7
    FLOAT_VECTOR3 = 8


class EntityMetaDataKey(Enum):
    FLAGS = 0
    HEALTH = 1  # minecart/boat
    VARIANT = 2
    COLOR = 3
    NAMETAG = 4
    OWNER_EID = 5
    TARGET_EID = 6
    AIR = 7
    POTION_COLOR = 8  # ARGB!
    POTION_AMBIENT = 9
    # 10 (byte)
    HURT_TIME = 11  # minecart/boat
    HURT_DIRECTION = 12  # minecart/boat
    PADDLE_TIME_LEFT = 13
    PADDLE_TIME_RIGHT = 14
    EXPERIENCE_VALUE = 15  # xp orb
    MINECART_DISPLAY_BLOCK = 16  # id | (data << 16)
    MINECART_DISPLAY_OFFSET = 17
    MINECART_HAS_DISPLAY = 18  # must be 1 for minecart to show block inside
    # 19..22
    ENDERMAN_HELD_ITEM_ID = 23
    ENDERMAN_HELD_ITEM_DAMAGE = 24
    ENTITY_AGE = 25
    # 27 (byte) player-specific flags
    # 28 (int) player "index"?
    BED_POSITION = 29
    FIREBALL_POWER_X = 30
    FIREBALL_POWER_Y = 31
    FIREBALL_POWER_Z = 32
    # 33 (unknown)
    # 34 (float) fishing bobber
    # 35 (float) fishing bobber
    # 36 (float) fishing bobber
    POTION_AUX_VALUE = 37
    LEAD_HOLDER_EID = 38
    SCALE = 39
    INTERACTIVE_TAG = 40  # button text
    NPC_SKIN_ID = 41
    URL_TAG = 42
    MAX_AIR = 43
    MARK_VARIANT = 44
    # 45 (byte) container stuff
    # 46 (int) container stuff
    # 47 (int) container stuff
    BLOCK_TARGET = 48  # ender crystal
    WITHER_INVULNERABLE_TICKS = 49
    WITHER_TARGET_1 = 50
    WITHER_TARGET_2 = 51
    WITHER_TARGET_3 = 52
    # 53 (short)
    BOUNDING_BOX_WIDTH = 54
    BOUNDING_BOX_HEIGHT = 55
    FUSE_LENGTH = 56
    RIDER_SEAT_POSITION = 57
    RIDER_ROTATION_LOCKED = 58
    RIDER_MAX_ROTATION = 59
    RIDER_MIN_ROTATION = 60
    AREA_EFFECT_CLOUD_RADIUS = 61
    AREA_EFFECT_CLOUD_WAITING = 62
    AREA_EFFECT_CLOUD_PARTICLE_ID = 63
    # 64 (int) shulker-related
    SHULKER_ATTACH_FACE = 65
    # 66 (short) shulker-related
    SHULKER_ATTACH_POS = 67
    TRADING_PLAYER_EID = 68
    # 69
    # 70 (byte) command-block
    COMMAND_BLOCK_COMMAND = 71
    COMMAND_BLOCK_LAST_OUTPUT = 72
    COMMAND_BLOCK_TRACK_OUTPUT = 73
    CONTROLLING_RIDER_SEAT_NUMBER = 74
    STRENGTH = 75
    MAX_STRENGTH = 76
    # 77 (int)
    # 78 (int)


class PlayerListType(Enum):
    ADD = 0
    REMOVE = 1


class WindowType(Enum):
    INVENTORY = 0
    OFFHAND = 119
    ARMOR = 120
    CREATIVE = 121
    HOTBAR = 122
    FIXED_INVENTORY = 123
    CURSOR = 124

    
class RecipeType(Enum):
    SHAPELESS = 0
    SHAPED = 1
    FURNACE = 2
    FURNACE_DATA = 3
    MULTI = 4
    SHULKER_BOX = 5


class BlockType(Enum):
    """Block IDs

    See https://minecraft.gamepedia.com/Java_Edition_data_values/Block_IDs
    """
    # TODO check ID
    AIR = 0
    STONE = 1
    GRASS = 2
    DIRT = 3
    COBBLESTONE = 4
    PLANKS = 5  # WOODEN_PLANKS
    SAPLING = 6
    BEDROCK = 7
    FLOWING_WATER = 8
    WATER = 9  # STILL_WATER
    FLOWING_LAVA = 10
    LAVA = 11  # STILL_LAVA
    SAND = 12
    GRAVEL = 13
    GOLD_ORE = 14
    IRON_ORE = 15
    COAL_ORE = 16
    LOG = 17  # WOOD
    LEAVES = 18
    SPONGE = 19
    GLASS = 20
    LAPIS_ORE = 21
    LAPIS_BLOCK = 22
    DISPENSER = 23
    SANDSTONE = 24
    NOTEBLOCK = 25  # NOTE_BLOCK
    BED = 26  # BED_BLOCK
    GOLDEN_RAIL = 27  # POWERED_RAIL
    DETECTOR_RAIL = 28
    STICKY_PISTON = 29
    WEB = 30  # COBWEB
    TALLGRASS = 31  # TALL_GRASS
    DEADBUSH = 32  # DEAD_BUSH
    PISTON = 33
    PISTON_HEAD = 34  # PISTONARMCOLLISION, PISTON_ARM_COLLISION
    WOOL = 35
    PISTON_EXTENSION = 36
    YELLOW_FLOWER = 37  # DANDELION
    RED_FLOWER = 38  # POPPY
    BROWN_MUSHROOM = 39
    RED_MUSHROOM = 40
    GOLD_BLOCK = 41
    IRON_BLOCK = 42
    DOUBLE_STONE_SLAB = 43
    STONE_SLAB = 44
    BRICK_BLOCK = 45
    TNT = 46
    BOOKSHELF = 47
    MOSSY_COBBLESTONE = 48  # MOSS_STONE
    OBSIDIAN = 49
    TORCH = 50
    FIRE = 51
    MOB_SPAWNER = 52  # MONSTER_SPAWNER
    OAK_STAIRS = 53   # WOODEN_STAIRS
    CHEST = 54
    REDSTONE_WIRE = 55
    DIAMOND_ORE = 56
    DIAMOND_BLOCK = 57
    CRAFTING_TABLE = 58  # WORKBENCH
    WHEAT = 59  # WHEAT_BLOCK
    FARMLAND = 60
    FURNACE = 61
    LIT_FURNACE = 62  # BURNING_FURNACE
    STANDING_SIGN = 63  # SIGN_POST
    WOODEN_DOOR = 64  # OAK_DOOR_BLOCK
    LADDER = 65
    RAIL = 66
    STONE_STAIRS = 67  # COBBLESTONE_STAIRS
    WALL_SIGN = 68
    LEVER = 69
    STONE_PRESSURE_PLATE = 70
    IRON_DOOR = 71
    WOODEN_PRESSURE_PLATE = 72
    REDSTONE_ORE = 73
    LIT_REDSTONE_ORE = 74  # GLOWING_REDSTONE_ORE
    UNLIT_REDSTONE_TORCH = 75
    REDSTONE_TORCH = 76  # LIT_REDSTONE_TORCH
    STONE_BUTTON = 77
    SNOW_LAYER = 78
    ICE = 79
    SNOW = 80  # SNOW_BLOCK
    CACTUS = 81
    CLAY = 82
    REEDS = 83  # SUGARCANE_BLOCK
    JUKEBOX = 84
    FENCE = 85
    PUMPKIN = 86
    NETHERRACK = 87
    SOUL_SAND = 88
    GLOWSTONE = 89
    PORTAL = 90
    LIT_PUMPKIN = 91  # JACK_O_LANTERN
    CAKE = 92
    UNPOWERED_REPEATER = 93  # REPEATER_BLOCK
    POWERED_REPEATER = 94
    STAINED_GLASS = 95  # INVISIBLEBEDROCK, INVISIBLE_BEDROCK
    TRAPDOOR = 96  # WOODEN_TRAPDOOR
    MONSTER_EGG = 97
    STONEBRICK = 98  # STONE_BRICK, STONE_BRICKS
    BROWN_MUSHROOM_BLOCK = 99
    RED_MUSHROOM_BLOCK = 100
    IRON_BARS = 101
    GLASS_PANE = 102
    MELON_BLOCK = 103
    PUMPKIN_STEM = 104
    MELON_STEM = 105
    VINE = 106  # VINES
    FENCE_GATE = 107  # OAK_FENCE_GATE
    BRICK_STAIRS = 108
    STONE_BRICK_STAIRS = 109
    MYCELIUM = 110
    WATERLILY = 111  # LILY_PAD, WATER_LILY
    NETHER_BRICK = 112
    NETHER_BRICK_FENCE = 113
    NETHER_BRICK_STAIRS = 114
    NETHER_WART = 115
    ENCHANTING_TABLE = 116  # ENCHANTMENT_TABLE
    BREWING_STAND = 117
    CAULDRON = 118
    END_PORTAL = 119
    END_PORTAL_FRAME = 120
    END_STONE = 121
    DRAGON_EGG = 122
    REDSTONE_LAMP = 123
    LIT_REDSTONE_LAMP = 124
    DOUBLE_WOODEN_SLAB = 125  # DROPPER
    WOODEN_SLAB = 126  # ACTIVATOR_RAIL
    COCOA = 127  # COCOA_BLOCK
    SANDSTONE_STAIRS = 128
    EMERALD_ORE = 129
    ENDER_CHEST = 130
    TRIPWIRE_HOOK = 131
    TRIPWIRE = 132  # TRIP_WIRE
    EMERALD_BLOCK = 133
    SPRUCE_STAIRS = 134
    BIRCH_STAIRS = 135
    JUNGLE_STAIRS = 136
    COMMAND_BLOCK = 137
    BEACON = 138
    COBBLESTONE_WALL = 139  # STONE_WALL
    FLOWER_POT = 140
    CARROTS = 141  # CARROT_BLOCK
    POTATOES = 142  # POTATO_BLOCK
    WOODEN_BUTTON = 143
    SKULL = 144  # MOB_HEAD_BLOCK
    ANVIL = 145
    TRAPPED_CHEST = 146
    LIGHT_WEIGHTED_PRESSURE_PLATE = 147
    HEAVY_WEIGHTED_PRESSURE_PLATE = 148
    UNPOWERED_COMPARATOR = 149  # COMPARATOR_BLOCK
    POWERED_COMPARATOR = 150
    DAYLIGHT_DETECTOR = 151  # DAYLIGHT_SENSOR
    REDSTONE_BLOCK = 152
    QUARTZ_ORE = 153  # NETHER_QUARTZ_ORE
    HOPPER = 154
    QUARTZ_BLOCK = 155
    QUARTZ_STAIRS = 156
    ACTIVATOR_RAIL = 157  # DOUBLE_WOODEN_SLAB
    DROPPER = 158  # WOODEN_SLAB
    STAINED_HARDENED_CLAY = 159  # STAINED_CLAY, TERRACOTTA
    STAINED_GLASS_PANE = 160
    LEAVES2 = 161
    LOG2 = 162  # WOOD2
    ACACIA_STAIRS = 163
    DARK_OAK_STAIRS = 164
    SLIME = 165  # SLIME_BLOCK
    BARRIER = 166
    IRON_TRAPDOOR = 167
    PRISMARINE = 168
    SEA_LANTERN = 169  # SEALANTERN
    HAY_BLOCK = 170  # HAY_BALE
    CARPET = 171
    HARDENED_CLAY = 172
    COAL_BLOCK = 173
    PACKED_ICE = 174
    DOUBLE_PLANT = 175
    STANDING_BANNER = 176
    WALL_BANNER = 177
    DAYLIGHT_DETECTOR_INVERTED = 178  # DAYLIGHT_SENSOR_INVERTED
    RED_SANDSTONE = 179
    RED_SANDSTONE_STAIRS = 180
    DOUBLE_STONE_SLAB2 = 181
    STONE_SLAB2 = 182
    SPRUCE_FENCE_GATE = 183
    BIRCH_FENCE_GATE = 184
    JUNGLE_FENCE_GATE = 185
    DARK_OAK_FENCE_GATE = 186
    ACACIA_FENCE_GATE = 187
    SPRUCE_FENCE = 188  # REPEATING_COMMAND_BLOCK
    BRICK_FENCE = 189  # CHAIN_COMMAND_BLOCK
    JUNGLE_FENCE = 190
    DARK_OAK_FENCE = 191
    ACACIA_FENCE = 192
    SPRUCE_DOOR = 193
    BIRCH_DOOR = 194
    JUNGLE_DOOR = 195
    ACACIA_DOOR = 196
    DARK_OAK_DOOR = 197
    END_ROD = 198  # GRASS_PATH
    CHORUS_PLANT = 199  # FRAME_BLOCK, ITEM_FRAME_BLOCK
    CHORUS_FLOWER = 200
    PURPUR_BLOCK = 201
    PURPUR_PILLAR = 202
    PURPUR_STAIRS = 203
    PURPUR_DOUBLE_SLAB = 204
    PURPUR_SLAB = 205  # UNDYED_SHULKER_BOX
    END_BRICKS = 206
    BEETROOTS = 207  # FROSTED_ICE
    GRASS_PATH = 208  # END_ROD
    END_GATEWAY = 209
    REPEATING_COMMAND_BLOCK = 210
    CHAIN_COMMAND_BLOCK = 211
    FROSTED_ICE = 212
    MAGMA = 213
    NETHER_WART_BLOCK = 214
    RED_NETHER_BRICK = 215
    BONE_BLOCK = 216
    STRUCTURE_VOID = 217
    OBSERVER = 218  # SHULKER_BOX
    WHITE_SHULKER_BOX = 219  # PURPLE_GLAZED_TERRACOTTA
    ORANGE_SHULKER_BOX = 220  # WHITE_GLAZED_TERRACOTTA
    MAGENTA_SHULKER_BOX = 221  # ORANGE_GLAZED_TERRACOTTA
    LIGHT_BLUE_SHULKER_BOX = 222  # MAGENTA_GLAZED_TERRACOTTA
    YELLOW_SHULKER_BOX = 223  # LIGHT_BLUE_GLAZED_TERRACOTTA
    LIME_SHULKER_BOX = 224  # YELLOW_GLAZED_TERRACOTTA
    PING_SHULKER_BOX = 225  # LIME_GLAZED_TERRACOTTA
    GRAY_SHULKER_BOX = 226  # PINK_GLAZED_TERRACOTTA
    SILVER_SHULKER_BOX = 227  # GRAY_GLAZED_TERRACOTTA
    CYAN_SHULKER_BOX = 228  # SILVER_GLAZED_TERRACOTTA
    PURPLE_SHULKER_BOX = 229  # CYAN_GLAZED_TERRACOTTA
    BLUE_SHULKER_BOX = 230
    BROWN_SHULKER_BOX = 231  # BLUE_GLAZED_TERRACOTTA
    GREEN_SHULKER_BOX = 232  # BROWN_GLAZED_TERRACOTTA
    RED_SHULKER_BOX = 233  # GREEN_GLAZED_TERRACOTTA
    BLACK_SHULKER_BOX = 234  # RED_GLAZED_TERRACOTTA
    WHITE_GLAZED_TERRACOTTA = 235  # BLACK_GLAZED_TERRACOTTA
    ORANGE_GLAZED_TERRACOTTA = 236  # CONCRETE
    MAGENTA_GLAZED_TERRACOTTA = 237  # CONCRETEPOWDER, CONCRETE_POWDER
    LIGHT_BLUE_GLAZED_TERRACOTTA = 238
    YELLOW_GLAZED_TERRACOTTA = 239
    LIME_GLAZED_TERRACOTTA = 240  # CHORUS_PLANT
    PINK_GLAZED_TERRACOTTA = 241  # STAINED_GLASS
    GRAY_GLAZED_TERRACOTTA = 242
    SILVER_GLAZED_TERRACOTTA = 243  # PODZOL
    CYAN_GLAZED_TERRACOTTA = 244  # BEETROOT_BLOCK
    PURPLE_GLAZED_TERRACOTTA = 245  # STONECUTTER
    BLUE_GLAZED_TERRACOTTA = 246  # GLOWINGOBSIDIAN, GLOWING_OBSIDIAN
    BROWN_GLAZED_TERRACOTTA = 247  # NETHERREACTOR, NETHER_REACTOR
    GREEN_GLAZED_TERRACOTTA = 248  # INFO_UPDATE
    RED_GLAZED_TERRACOTTA = 249  # INFO_UPDATE2
    BLACK_GLAZED_TERRACOTTA = 250  # MOVINGBLOCK, MOVING_BLOCK
    CONCRETE = 251  # OBSERVER
    CONCRETE_POWDER = 252  # STRUCTURE_BLOCK
    UNUSED_FD = 253
    UNUSED_FE = 254
    STRUCTURE_BLOCK = 255
