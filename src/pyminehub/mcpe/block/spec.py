from itertools import combinations
from typing import NamedTuple, FrozenSet, Optional, Tuple, List, Sequence, Iterator

from pyminehub.mcpe.const import ItemType, BlockType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.value import Item, Block, PlacedBlock

__all__ = [
    'BlockSpec',
    'AirBlockSpec',
    'ToExtendUpwardBlockSpec',
    'SlabBlockSpec',
    'SnowLayerBlockSpec',
    'LadderBlockSpec',
    'FenceGateBlockSpec',
    'TrapDoorBlockSpec',
    'CarpetBlockSpec',
    'DoublePlantBlockSpec',
    'DoorBlockSpec',
    'EndRodBlockSpec',
    'ToggleBlockSpec',
    'TripwireHookBlockSpec',
    'DaylightDetectorBlockSpec',
    'TorchBlockSpec',
    'RailBlockSpec',
    'ChestBlockSpec'
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


class BlockSpec:

    def __init__(
            self,
            item_type: Optional[ItemType],
            max_layer_num: int=1,
            can_be_broken: bool=True,
            can_pass: bool=False,
            can_be_attached_on_ground: bool=False,
            is_switchable: bool=False
    ) -> None:
        self._item_type = item_type
        self._max_layer_num = max_layer_num
        self._can_be_broken = can_be_broken
        self._can_pass = can_pass
        self._can_be_attached_on_ground = can_be_attached_on_ground
        self._is_switchable = is_switchable

    @property
    def item_type(self) -> Optional[ItemType]:
        return self._item_type

    @property
    def has_layer(self) -> bool:
        return self._max_layer_num > 1

    @property
    def max_layer_num(self) -> int:
        return self._max_layer_num

    @property
    def can_be_broken(self) -> bool:
        return self._can_be_broken

    @property
    def can_be_attached_on_ground(self) -> bool:
        return self._can_be_attached_on_ground

    @property
    def is_switchable(self) -> bool:
        return self._is_switchable

    def is_on(self, block: Block) -> bool:
        assert self._is_switchable
        return False

    def can_pass(self, block: Block) -> bool:
        return self._can_pass

    def can_be_overridden_by(self, block: Block) -> bool:
        return False

    def get_link_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        return ()

    def get_break_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        return Vector3(0, 0, 0),

    def to_item(self, block_data: int) -> List[Item]:
        return [Item.create(self.item_type, 1, block_data)] if self.item_type is not None else []

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        assert self.has_layer > 1
        return None

    def get_switch_position(self, block: Block) -> Vector3[int]:
        return Vector3(0, 0, 0)

    def switch(self, block: Block) -> Block:
        assert self.is_switchable
        return block

    def get_additional_blocks(self, block: Block, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        return PlacedBlock(Vector3(0, 0, 0), block),

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL

    def can_be_attached_on(self, block: Block) -> bool:
        return True


class AirBlockSpec(BlockSpec):

    def __init__(self) -> None:
        super().__init__(None, can_be_broken=False, can_pass=True)

    def can_be_overridden_by(self, block: Block) -> bool:
        return True

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE


class ToExtendUpwardBlockSpec(BlockSpec):

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_BOTTOM


class SlabBlockSpec(BlockSpec):

    _SLAB_TYPE_MASK = 0b111
    _IS_UPPER_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType], full_stacked_block_type: BlockType) -> None:
        super().__init__(item_type, 2)
        self._full_stacked_block_type = full_stacked_block_type

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        """
        >>> spec = SlabBlockSpec(None, BlockType.DOUBLE_WOODEN_SLAB)
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


class SnowLayerBlockSpec(ToExtendUpwardBlockSpec):

    def __init__(self) -> None:
        super().__init__(None, max_layer_num=8, can_pass=True, can_be_attached_on_ground=True)

    def stack_layer(self, base_block: Block, stacked_block: Block, face: Face) -> Optional[Block]:
        """
        >>> spec = SnowLayerBlockSpec()
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


class LadderBlockSpec(BlockSpec):

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
        super().__init__(ItemType.LADDER, can_pass=True)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return self._CONNECTOR[block.data]

    def can_be_attached_on(self, block: Block) -> bool:
        return block.type in self._CAN_BE_ATTACHED


class FenceGateBlockSpec(ToExtendUpwardBlockSpec):

    _DOES_OPEN_MASK = 0b100

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_be_attached_on_ground=True, is_switchable=True)

    def is_on(self, block: Block) -> bool:
        return bool(block.data & self._DOES_OPEN_MASK)

    def can_pass(self, block: Block) -> bool:
        return self.is_on(block)

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._DOES_OPEN_MASK)


class TrapDoorBlockSpec(BlockSpec):

    _DOES_OPEN_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True, is_switchable=True)

    def is_on(self, block: Block) -> bool:
        return bool(block.data & self._DOES_OPEN_MASK)

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._DOES_OPEN_MASK)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL


class CarpetBlockSpec(ToExtendUpwardBlockSpec):

    def __init__(self) -> None:
        super().__init__(ItemType.CARPET, can_pass=True, can_be_attached_on_ground=True)


class DoublePlantBlockSpec(ToExtendUpwardBlockSpec):

    _IS_UPPER_MASK = 0b1000

    def _is_upper(self, block: Block) -> bool:
        return bool(block.data & self._IS_UPPER_MASK)

    def get_break_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        if self._is_upper(block):
            return Vector3(0, 0, 0),
        else:
            return Vector3(0, 1, 0), Vector3(0, 0, 0)

    def get_additional_blocks(self, block: Block, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        return PlacedBlock(Vector3(0, 0, 0), block), PlacedBlock(Vector3(0, 1, 0), block.copy(data=self._IS_UPPER_MASK))


class DoorBlockSpec(ToExtendUpwardBlockSpec):

    # set to the upper part
    _IS_UPPER_MASK = 0b1000
    _IS_RIGHT_SIDE_MASK = 0b1

    # set to the lower part
    _DOES_OPEN_MASK = 0b100
    _FACE_MASK = 0b11

    _LEFT_SIDE = {
        0: Vector3(0, 0, -1),
        1: Vector3(1, 0, 0),
        2: Vector3(0, 0, 1),
        3: Vector3(-1, 0, 0)
    }

    _BREAK_ORDER = (Vector3(0, 1, 0), Vector3(0, 0, 0))

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True, is_switchable=True)

    def is_on(self, block: Block) -> bool:
        return not (block.data & self._IS_UPPER_MASK) and bool(block.data & self._DOES_OPEN_MASK)

    def _get_face(self, block: Block) -> int:
        return block.data & self._FACE_MASK

    def _is_upper_part(self, block: Block) -> bool:
        return bool(block.data & self._IS_UPPER_MASK)

    def _is_right_side(self, block: Block) -> bool:
        assert self._is_upper_part(block)
        return bool(block.data & self._IS_RIGHT_SIDE_MASK)

    def get_link_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        """
        >>> spec = DoorBlockSpec(None)
        >>> spec.get_link_target(Block.create(BlockType.WOODEN_DOOR_BLOCK, 0))
        (Vector3(x=0, y=0, z=-1), Vector3(x=0, y=1, z=-1))
        >>> spec.get_link_target(Block.create(BlockType.WOODEN_DOOR_BLOCK, 1))
        (Vector3(x=1, y=0, z=0), Vector3(x=1, y=1, z=0))
        >>> spec.get_link_target(Block.create(BlockType.WOODEN_DOOR_BLOCK, 2))
        (Vector3(x=0, y=0, z=1), Vector3(x=0, y=1, z=1))
        >>> spec.get_link_target(Block.create(BlockType.WOODEN_DOOR_BLOCK, 3))
        (Vector3(x=-1, y=0, z=0), Vector3(x=-1, y=1, z=0))
        """
        assert not self._is_upper_part(block)
        left_side = self._LEFT_SIDE[self._get_face(block)]
        return left_side, left_side + (0, 1, 0)

    def get_break_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        dy = -1 if self._is_upper_part(block) else 0
        return tuple(p + (0, dy, 0) for p in self._BREAK_ORDER)

    def get_switch_position(self, block: Block) -> Vector3[int]:
        dy = -1 if self._is_upper_part(block) else 0
        return Vector3(0, dy, 0)

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._DOES_OPEN_MASK)

    def get_additional_blocks(self, block: Block, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        assert len(linked_blocks) == 2
        left_side_lower_block, left_side_upper_block = linked_blocks
        right_side_mask = 0
        if left_side_lower_block.type == block.type and self._get_face(left_side_lower_block) == self._get_face(block):
            if not self._is_right_side(left_side_upper_block):
                right_side_mask = self._IS_RIGHT_SIDE_MASK
        data = self._IS_UPPER_MASK | right_side_mask
        return PlacedBlock(Vector3(0, 0, 0), block), PlacedBlock(Vector3(0, 1, 0), block.copy(data=data))


class EndRodBlockSpec(BlockSpec):

    _BASE_SIDE = {
        0: Vector3(0, 1, 0),
        1: Vector3(0, -1, 0),
        2: Vector3(0, 0, -1),
        3: Vector3(0, 0, 1),
        4: Vector3(-1, 0, 0),
        5: Vector3(1, 0, 0)
    }

    def __init__(self) -> None:
        super().__init__(ItemType.END_ROD)

    def get_link_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        return self._BASE_SIDE[block.data],

    def get_additional_blocks(self, block: Block, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        assert len(linked_blocks) == 1
        base_side_block = linked_blocks[0]
        if base_side_block.type == block.type and base_side_block.data == block.data:
            block = block.copy(data=block.data ^ 1)
        return PlacedBlock(Vector3(0, 0, 0), block),


class ToggleBlockSpec(BlockSpec):

    _TOGGLE_MASK = 0b1000

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True, is_switchable=True)

    def is_on(self, block: Block) -> bool:
        return bool(block.data & self._TOGGLE_MASK)

    def switch(self, block: Block) -> Block:
        return block.copy(data=block.data ^ self._TOGGLE_MASK)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL


class TripwireHookBlockSpec(BlockSpec):

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_SIDE


class DaylightDetectorBlockSpec(BlockSpec):

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, is_switchable=True)

    def is_on(self, block: Block) -> bool:
        return block.type is BlockType.DAYLIGHT_DETECTOR_INVERTED

    def switch(self, block: Block) -> Block:
        block_type = BlockType.DAYLIGHT_DETECTOR_INVERTED \
            if block.type is BlockType.DAYLIGHT_DETECTOR else BlockType.DAYLIGHT_DETECTOR
        return block.copy(block_type=block_type)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_BOTTOM


class TorchBlockSpec(BlockSpec):

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True)

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL - _CONNECTOR_TOP


def _get_neighbour_position(center: Vector3[int]) -> Tuple[Vector3[int], ...]:
    return tuple(
        center + face.direction + (0, y, 0)
        for y in (-1, 0, 1)
        for face in (Face.SOUTH, Face.NORTH, Face.EAST, Face.WEST)
    )


_NEIGHBOUR = _get_neighbour_position(Vector3(0, 0, 0))
_SURROUNDING = _NEIGHBOUR + tuple(set(p for p in _NEIGHBOUR for p in _get_neighbour_position(p)))

_RailType = NamedTuple('RailType', [
    ('data', int),
    ('connector', Tuple[Vector3[int], Vector3[int]])
])

_RAIL_TYPE = {
    0: _RailType(0, (Vector3(0, 0, -1), Vector3(0, 0, 1))),
    1: _RailType(1, (Vector3(-1, 0, 0), Vector3(1, 0, 0))),
    2: _RailType(2, (Vector3(-1, 0, 0), Vector3(1, 1, 0))),
    3: _RailType(3, (Vector3(-1, 1, 0), Vector3(1, 0, 0))),
    4: _RailType(4, (Vector3(0, 1, -1), Vector3(0, 0, 1))),
    5: _RailType(5, (Vector3(0, 0, -1), Vector3(0, 1, 1))),
    6: _RailType(6, (Vector3(0, 0, 1), Vector3(1, 0, 0))),
    7: _RailType(7, (Vector3(0, 0, 1), Vector3(-1, 0, 0))),
    8: _RailType(8, (Vector3(0, 0, -1), Vector3(-1, 0, 0))),
    9: _RailType(9, (Vector3(0, 0, -1), Vector3(1, 0, 0))),
}

_RAIL_BLOCK_TYPES = (
    BlockType.RAIL,
    BlockType.GOLDEN_RAIL,
    BlockType.DETECTOR_RAIL,
    BlockType.DETECTOR_RAIL
)


class _RailNetwork:

    def __init__(self, linked_blocks: Iterator[Tuple[Vector3[int], Block]]) -> None:
        self._blocks = dict((position, block) for position, block in linked_blocks)
        self._rail_positions = self.get_rail_positions_by_neighbour(Vector3(0, 0, 0))

    @property
    def has_rail_by_neighbour(self) -> bool:
        return len(self._rail_positions) > 0

    def get_block(self, position: Vector3[int]) -> Block:
        return self._blocks[position]

    def get_rail_positions_by_neighbour(self, center: Vector3[int]) -> FrozenSet[Vector3[int]]:
        neighbour = _get_neighbour_position(center)
        return frozenset(position for position in neighbour if self._blocks[position].type in _RAIL_BLOCK_TYPES)

    def has_connectable_rail_at(self, position: Vector3[int]) -> bool:
        if position not in self._rail_positions:
            return False
        if self._is_connected_full(position):
            return False
        return True

    def _is_connected_full(self, position: Vector3[int]) -> bool:
        return len(self.get_conntected_connector(position)) == 2

    def get_conntected_connector(self, position: Vector3[int]) -> List[Vector3[int]]:
        connected = []
        rail_type = _RAIL_TYPE[self._blocks[position].data]
        for connector in rail_type.connector:
            block = self._blocks[position + connector]
            c = connector
            if block.type not in _RAIL_BLOCK_TYPES:
                if connector.y != 0:
                    continue
                c = connector + (0, -1, 0)
                block = self._blocks[position + c]
                if block.type not in _RAIL_BLOCK_TYPES:
                    continue
            rail_type = _RAIL_TYPE[self._blocks[position + c].data]
            if - (c if c.y != 1 else c * (1, 0, 1)) not in rail_type.connector:
                continue
            connected.append(connector)
        return connected


class RailBlockSpec(BlockSpec):

    def __init__(self, item_type: Optional[ItemType]) -> None:
        super().__init__(item_type, can_pass=True, can_be_attached_on_ground=True)

    def can_be_overridden_by(self, block: Block) -> bool:
        return block.type in _RAIL_BLOCK_TYPES

    def get_link_target(self, block: Block) -> Tuple[Vector3[int], ...]:
        return _SURROUNDING

    def get_additional_blocks(self, block: Block, linked_blocks: Sequence[Block]) -> Tuple[PlacedBlock, ...]:
        network = _RailNetwork(zip(_SURROUNDING, linked_blocks))
        data = self._get_block_data(network, block.type == BlockType.RAIL)
        blocks = [PlacedBlock(Vector3(0, 0, 0), block.copy(data=data))]
        rail_type = _RAIL_TYPE[data]
        for connector in rail_type.connector:
            updated = self._update_neighbour(network, connector)
            if updated:
                blocks.append(updated)
        return tuple(blocks)

    @staticmethod
    def _get_block_data(network: _RailNetwork, has_corner: bool) -> int:
        if not network.has_rail_by_neighbour:
            return 0
        for data in (6, 7, 8, 9) if has_corner else ():
            connector = _RAIL_TYPE[data].connector
            for c1, c2 in combinations(connector + tuple(c + (0, -1, 0) for c in connector), 2):
                if network.has_connectable_rail_at(c1) and network.has_connectable_rail_at(c2):
                    return data
        for data in (2, 3, 4, 5):
            connector = tuple(filter(lambda c: c.y == 1, _RAIL_TYPE[data].connector))
            assert len(connector) == 1
            if network.has_connectable_rail_at(connector[0]):
                return data
        for data in (0, 1):
            connector = _RAIL_TYPE[data].connector
            for c in connector:
                if network.has_connectable_rail_at(c):
                    return data
                if network.has_connectable_rail_at(c + (0, -1, 0)):
                    return data
        return 0

    def _update_neighbour(self, network: _RailNetwork, position: Vector3[int]) -> Optional[PlacedBlock]:
        block = network.get_block(position)
        if block.type not in _RAIL_BLOCK_TYPES:
            position += (0, -1, 0)
            block = network.get_block(position)
            if block.type not in _RAIL_BLOCK_TYPES:
                return None
        if - position in _RAIL_TYPE[block.data].connector:
            return None
        connected_connector = network.get_conntected_connector(position)
        if len(connected_connector) == 2:
            return None
        has_corner = block.type == BlockType.RAIL
        if len(connected_connector) > 0:
            assert len(connected_connector) == 1
            connected_connector = connected_connector[0]
            c = - position if position.y != 1 else position * (-1, 0, -1)
            for data in range(10) if has_corner else range(6):
                data, connector = _RAIL_TYPE[data]
                if connected_connector not in connector:
                    continue
                if c in connector:
                    return PlacedBlock(position, block.copy(data=data))
            return None
        else:
            c = - position if position.y != 1 else position * (-1, 0, -1)
            for data in range(10) if has_corner else range(6):
                data, connector = _RAIL_TYPE[data]
                if c in connector:
                    return PlacedBlock(position, block.copy(data=data))
            return None

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_BOTTOM


class ChestBlockSpec(BlockSpec):

    def female_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_NONE

    def male_connector(self, block: Block) -> _Connector:
        return _CONNECTOR_ALL


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
