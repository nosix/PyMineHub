from typing import List, Optional, FrozenSet

from pyminehub.mcpe.const import BlockType, ItemType
from pyminehub.mcpe.geometry import Face
from pyminehub.mcpe.value import Item, Block

__all__ = [
    'CompositeBlock'
]


_Connector = FrozenSet[Face]

_CONNECTOR_NONE = frozenset()
_CONNECTOR_BOTTOM = frozenset([Face.BOTTOM])
_CONNECTOR_TOP = frozenset([Face.TOP])
_CONNECTOR_SOUTH = frozenset([Face.SOUTH])
_CONNECTOR_NORTH = frozenset([Face.NORTH])
_CONNECTOR_EAST = frozenset([Face.EAST])
_CONNECTOR_WEST = frozenset([Face.WEST])
_CONNECTOR_SIDE = frozenset([Face.SOUTH, Face.NORTH, Face.EAST, Face.WEST])
_CONNECTOR_ALL = frozenset([Face.BOTTOM, Face.TOP, Face.SOUTH, Face.NORTH, Face.EAST, Face.WEST])


class _BlockSpec:

    def __init__(
            self,
            item_type: Optional[ItemType],
            max_layer_num: int=1,
            can_be_attached_on_ground: bool=False,
            is_switchable: bool=False
    ) -> None:
        self._item_type = item_type
        self._max_layer_num = max_layer_num
        self._can_be_attached_on_ground = can_be_attached_on_ground
        self._is_switchable = is_switchable

    @property
    def item_type(self) -> Optional[ItemType]:
        return self._item_type

    @property
    def max_layer_num(self) -> int:
        return self._max_layer_num

    @property
    def can_be_attached_on_ground(self) -> bool:
        return self._can_be_attached_on_ground

    @property
    def is_switchable(self) -> bool:
        return self._is_switchable

    def to_item(self, block_data: int) -> List[Item]:
        return [Item.create(self.item_type, 1, block_data)] if self.item_type is not None else []

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()

    def switch(self, block: Block) -> Block:
        raise NotImplementedError()

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL

    def can_be_attached_on(self, block: Block) -> bool:
        return True


class _AirBlockSpec(_BlockSpec):

    def __init__(self) -> None:
        super().__init__(None)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()

    def switch(self, block: Block) -> Block:
        raise NotImplementedError()

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE


class _SlabBlockSpec(_BlockSpec):

    _SLAB_TYPE_MASK = 0b111
    _IS_UPPER_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType], full_stacked_block_type: BlockType) -> None:
        super().__init__(item_type, 2)
        self._full_stacked_block_type = full_stacked_block_type

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        """
        >>> spec = _SlabBlockSpec(None, BlockType.DOUBLE_WOODEN_SLAB)
        >>> block_type = BlockType.WOODEN_SLAB
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8), Face.TOP)
        Block(type=<BlockType.DOUBLE_WOODEN_SLAB: 157>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 8), Block.create(block_type, 0), Face.BOTTOM)
        Block(type=<BlockType.DOUBLE_WOODEN_SLAB: 157>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 8), Block.create(block_type, 0), Face.TOP)
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8), Face.BOTTOM)
        >>> spec.stack_layer(Block.create(block_type, 0, neighbors=True), Block.create(block_type, 8), Face.TOP)
        Block(type=<BlockType.DOUBLE_WOODEN_SLAB: 157>, aux_value=0)
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 8, neighbors=True), Face.TOP)
        Block(type=<BlockType.DOUBLE_WOODEN_SLAB: 157>, aux_value=16)
        >>> spec.stack_layer(\\
        ...     Block.create(block_type, 0, neighbors=True), Block.create(block_type, 8, neighbors=False), Face.TOP)
        Block(type=<BlockType.DOUBLE_WOODEN_SLAB: 157>, aux_value=0)
        """
        slab_type = stacked_block.data & self._SLAB_TYPE_MASK
        if slab_type != base_block.data & self._SLAB_TYPE_MASK:
            return base_block
        is_upper = stacked_block.data & self._IS_UPPER_MASK
        if is_upper != base_block.data & self._IS_UPPER_MASK:
            if (face is Face.BOTTOM and is_upper) or (face is Face.TOP and not is_upper):
                return None
            return Block.create(self._full_stacked_block_type, slab_type, **stacked_block.flags)
        return None

    def switch(self, block: Block) -> Block:
        raise NotImplementedError()

    def female_connector(self, block: Block) -> _Connector:
        if block.data & self._IS_UPPER_MASK:
            return _CONNECTOR_ALL - _CONNECTOR_BOTTOM
        else:
            return _CONNECTOR_ALL - _CONNECTOR_TOP

    def male_connector(self, block: Block):
        if block.data & self._IS_UPPER_MASK:
            return _CONNECTOR_ALL - _CONNECTOR_BOTTOM
        else:
            return _CONNECTOR_ALL - _CONNECTOR_TOP


class _SnowLayerBlockSpec(_BlockSpec):

    def __init__(self) -> None:
        super().__init__(None, max_layer_num=8, can_be_attached_on_ground=True)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        """
        >>> spec = _SnowLayerBlockSpec()
        >>> block_type = BlockType.SNOW_LAYER
        >>> spec.stack_layer(Block.create(block_type, 0), Block.create(block_type, 0), Face.TOP)
        Block(type=<BlockType.SNOW_LAYER: 78>, aux_value=1)
        >>> spec.stack_layer(Block.create(block_type, 1), Block.create(block_type, 0), Face.TOP)
        Block(type=<BlockType.SNOW_LAYER: 78>, aux_value=2)
        >>> spec.stack_layer(Block.create(block_type, 5), Block.create(block_type, 0), Face.TOP)
        Block(type=<BlockType.SNOW_LAYER: 78>, aux_value=6)
        >>> spec.stack_layer(Block.create(block_type, 6), Block.create(block_type, 0), Face.TOP)
        Block(type=<BlockType.SNOW: 80>, aux_value=0)
        """
        layer_index = base_block.data + 1
        if layer_index != self.max_layer_num - 1:
            return Block.create(BlockType.SNOW_LAYER, layer_index, **stacked_block.flags)
        else:
            return Block.create(BlockType.SNOW, 0, **stacked_block.flags)

    def switch(self, block: Block) -> Block:
        raise NotImplementedError()

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_BOTTOM


class _LadderBlockSpec(_BlockSpec):

    _CAN_BE_ATTACHED = (
        BlockType.PLANKS,

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
        BlockType.LOG,
        BlockType.LOG2,

        BlockType.MELON_BLOCK,
        BlockType.PUMPKIN,
        BlockType.LIT_PUMPKIN,

        BlockType.SNOW,
        BlockType.PACKED_ICE,

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

        BlockType.REDSTONE_LAMP,
        BlockType.OBSERVER,
        BlockType.PISTON,
        BlockType.STICKY_PISTON,
    )

    _CONNECTOR = {
        2: _CONNECTOR_NORTH,
        3: _CONNECTOR_SOUTH,
        4: _CONNECTOR_WEST,
        5: _CONNECTOR_EAST
    }

    def __init__(self) -> None:
        super().__init__(ItemType.LADDER)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()

    def switch(self, block: Block) -> Block:
        raise NotImplementedError()

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return self._CONNECTOR[block.data]

    def can_be_attached_on(self, block: Block) -> bool:
        return block.type in self._CAN_BE_ATTACHED


class _FenceGateBlockSpec(_BlockSpec):

    _DOES_OPEN_MASK = 0b100

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_be_attached_on_ground=True, is_switchable=True)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._DOES_OPEN_MASK)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_BOTTOM


class _TrapDoorBlockSpec(_BlockSpec):

    _DOES_OPEN_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, is_switchable=True)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        raise NotImplementedError()

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._DOES_OPEN_MASK)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL


_block_specs = {
    BlockType.AIR: _AirBlockSpec(),
    BlockType.GRASS: _BlockSpec(ItemType.DIRT),
    BlockType.STONE_SLAB: _SlabBlockSpec(ItemType.STONE_SLAB, BlockType.DOUBLE_STONE_SLAB),
    BlockType.WOODEN_SLAB: _SlabBlockSpec(ItemType.WOODEN_SLAB, BlockType.DOUBLE_WOODEN_SLAB),
    BlockType.STONE_SLAB2: _SlabBlockSpec(ItemType.STONE_SLAB2, BlockType.DOUBLE_STONE_SLAB2),
    BlockType.SNOW_LAYER: _SnowLayerBlockSpec(),
    BlockType.LADDER: _LadderBlockSpec(),
    BlockType.TRAPDOOR: _TrapDoorBlockSpec(ItemType.TRAPDOOR),
}


_blocks = [
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

    BlockType.IRON_TRAPDOOR,

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
    BlockType.DOUBLE_WOODEN_SLAB,
    BlockType.DOUBLE_STONE_SLAB2,
]

_fence_gate_blocks = [
    BlockType.FENCE_GATE,
    BlockType.SPRUCE_FENCE_GATE,
    BlockType.BIRCH_FENCE_GATE,
    BlockType.JUNGLE_FENCE_GATE,
    BlockType.ACACIA_FENCE_GATE,
    BlockType.DARK_OAK_FENCE_GATE,
]

for _block_type in _blocks:
    _block_specs[_block_type] = _BlockSpec(ItemType(_block_type.value))

for _block_type in _fence_gate_blocks:
    _block_specs[_block_type] = _FenceGateBlockSpec(ItemType(_block_type.value))


class CompositeBlock:
    """CompositeBlock joins block value and block specification"""

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

    @property
    def can_be_attached_on_ground(self) -> bool:
        return self._block_spec.can_be_attached_on_ground

    @property
    def is_switchable(self) -> bool:
        return self._block_spec.is_switchable

    def to_item(self) -> List[Item]:
        return self._block_spec.to_item(self._block.data)

    def stack_on(self, base_block: Block, face: Face) -> Optional[Block]:
        return self._block_spec.stack_layer(base_block, self._block, face)

    def switch(self) -> Block:
        return self._block_spec.switch(self._block)

    def can_be_attached_on(self, base_block: Block, face: Face) -> bool:
        if face.inverse not in self._block_spec.male_connector(self._block):
            return False
        base_block_spec = _block_specs[base_block.type]
        if face not in base_block_spec.female_connector(base_block):
            return False
        return self._block_spec.can_be_attached_on(base_block)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
