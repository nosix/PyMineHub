from typing import Optional, Tuple

from pyminehub.mcpe.const import ItemType, BlockType
from pyminehub.mcpe.geometry import Vector3, Face
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

    def to_block(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float],
            **flags: bool
    ) -> Optional[Block]:
        if self.block_type is None:
            return None
        block_data = self.to_block_data(item_data, attached_face, horizontal_player_face, click_position)
        return Block.create(self.block_type, block_data, **flags)

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        raise NotImplementedError()


class DefaultItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        return item_data


class DirectionalItemSpec(ItemSpec):

    def __init__(self, block_type: Optional[BlockType], max_quantity: int, directional_data: Tuple[int, ...]) -> None:
        super().__init__(block_type, max_quantity)
        self._directional_data = directional_data

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = DirectionalItemSpec(None, 0, (0, ))
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 0, 0, 0]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [0, 0, 0, 0]
        >>> spec.to_block_data(0, Face.EAST, Face.WEST, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST, Vector3(1.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH, Vector3(0.5, 0.5, 1.0))
        8
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH, Vector3(0.5, 0.5, 0.0))
        8

        >>> spec = DirectionalItemSpec(None, 0, (1, 2))
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(1, Face.TOP, f, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [1, 1, 1, 1]
        >>> list(spec.to_block_data(2, Face.BOTTOM, f, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 2, 2, 2]
        >>> spec.to_block_data(0, Face.EAST, Face.WEST, Vector3(0.0, 0.5, 0.5))
        0
        >>> spec.to_block_data(1, Face.EAST, Face.WEST, Vector3(0.0, 0.5, 0.5))
        5
        >>> spec.to_block_data(2, Face.WEST, Face.EAST, Vector3(1.0, 0.5, 0.5))
        6
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH, Vector3(0.5, 0.5, 1.0))
        0
        >>> spec.to_block_data(1, Face.NORTH, Face.SOUTH, Vector3(0.5, 0.5, 1.0))
        9
        >>> spec.to_block_data(2, Face.SOUTH, Face.NORTH, Vector3(0.5, 0.5, 0.0))
        10
        """
        if item_data not in self._directional_data:
            return item_data
        if attached_face in (Face.EAST, Face.WEST):
            return 4 + item_data
        if attached_face in (Face.NORTH, Face.SOUTH):
            return 8 + item_data
        return item_data


class StairItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = StairItemSpec(None, 0)
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [4, 5, 6, 7]
        >>> list(spec.to_block_data(0, f.inverse, f, Vector3(0.5, 0.25, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, f.inverse, f, Vector3(0.5, 0.75, 0.5)) for f in faces)
        [4, 5, 6, 7]
        """
        assert item_data == 0
        if attached_face is Face.TOP or (attached_face is not Face.BOTTOM and click_position.y < 0.5):
            return Face.WEST.value - horizontal_player_face.value
        else:
            return 4 + Face.WEST.value - horizontal_player_face.value


class TerracottaItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = TerracottaItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.SOUTH, Face.WEST, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, f.inverse, f, Vector3(0.5, 0.5, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.WEST, f, Vector3(1.0, 0.5, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [2, 3]
        >>> list(spec.to_block_data(0, Face.NORTH, f, Vector3(0.5, 0.5, 1.0)) for f in [Face.WEST, Face.EAST])
        [4, 5]
        >>> list(spec.to_block_data(0, Face.EAST, f, Vector3(0.0, 0.5, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [2, 3]
        >>> list(spec.to_block_data(0, Face.SOUTH, f, Vector3(0.5, 0.5, 0.0)) for f in [Face.WEST, Face.EAST])
        [4, 5]
        """
        assert item_data == 0
        return horizontal_player_face.inverse.value


class JackOLanternSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.SOUTH: 0,
        Face.WEST: 1,
        Face.NORTH: 2,
        Face.EAST: 3
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            horizontal_player_face: Face,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = JackOLanternSpec(None, 0)
        >>> faces = [Face.SOUTH, Face.WEST, Face.NORTH, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.EAST, f, Vector3(0.0, 0.5, 0.5)) for f in [Face.SOUTH, Face.NORTH])
        [0, 2]
        >>> list(spec.to_block_data(0, Face.WEST, f, Vector3(1.0, 0.5, 0.5)) for f in [Face.SOUTH, Face.NORTH])
        [0, 2]
        >>> list(spec.to_block_data(0, Face.SOUTH, f, Vector3(0.5, 0.5, 0.0)) for f in [Face.WEST, Face.EAST])
        [1, 3]
        >>> list(spec.to_block_data(0, Face.NORTH, f, Vector3(0.5, 0.5, 1.0)) for f in [Face.WEST, Face.EAST])
        [1, 3]
        """
        assert item_data == 0
        return self._FACE_TO_DATA[horizontal_player_face]


_item_specs = {
    ItemType.AIR: DefaultItemSpec(None, 0),
    ItemType.HAY_BLOCK: DirectionalItemSpec(BlockType.HAY_BLOCK, 64, (0,)),
    ItemType.BONE_BLOCK: DirectionalItemSpec(BlockType.BONE_BLOCK, 64, (0,)),
    ItemType.QUARTZ_BLOCK: DirectionalItemSpec(BlockType.QUARTZ_BLOCK, 64, (1, 2)),
    ItemType.PURPUR_BLOCK: DirectionalItemSpec(BlockType.PURPUR_BLOCK, 64, (2,)),
    ItemType.LOG: DirectionalItemSpec(BlockType.LOG, 64, (0, 1, 2, 3)),
    ItemType.LOG2: DirectionalItemSpec(BlockType.LOG2, 64, (0, 1)),
    ItemType.LIT_PUMPKIN: JackOLanternSpec(BlockType.LIT_PUMPKIN, 64),
}

_block_items = [
    # Construction

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

    ItemType.TRAPDOOR,
    ItemType.IRON_TRAPDOOR,

    ItemType.IRON_BARS,

    ItemType.GLASS,
    ItemType.STAINED_GLASS,
    ItemType.GLASS_PANE,
    ItemType.STAINED_GLASS_PANE,

    ItemType.LADDER,

    ItemType.STONE_SLAB,  # TODO layer
    ItemType.WOODEN_SLAB,  # TODO layer
    ItemType.STONE_SLAB2,  # TODO layer

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

    ItemType.CARPET,  # TODO layer

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
    ItemType.PUMPKIN,

    ItemType.TALLGRASS,
    ItemType.DOUBLE_PLANT,
    ItemType.YELLOW_FLOWER,
    ItemType.FLOWER,

    ItemType.VINE,

    ItemType.SNOW,
    ItemType.ICE,
    ItemType.PACKED_ICE,
    ItemType.SNOW_LAYER,  # TODO layer

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


for _item_type in _block_items:
    _item_specs[_item_type] = DefaultItemSpec(BlockType(_item_type.value), 64)

for _item_type in _stairs_block_items:
    _item_specs[_item_type] = StairItemSpec(BlockType(_item_type.value), 64)

for _item_type in _terracotta_block_items:
    _item_specs[_item_type] = TerracottaItemSpec(BlockType(_item_type.value), 64)


def get_item_spec(item_type: ItemType) -> ItemSpec:
    return _item_specs[item_type]


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
