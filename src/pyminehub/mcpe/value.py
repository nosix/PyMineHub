from typing import Dict, NamedTuple, Optional, Tuple, Union
from uuid import UUID

from pyminehub.binutil.converter import dict_to_flags, flags_to_dict
from pyminehub.mcpe.const import *
from pyminehub.mcpe.geometry import *

__all__ = [
    'PlayerID',
    'EntityUniqueID',
    'EntityRuntimeID',
    'GameRule',
    'Attribute',
    'AdventureSettings',
    'MetaDataValue',
    'EntityMetaData',
    'EntityMetaDataFlagValue',
    'EntityAttribute',
    'EntityLink',
    'Item',
    'Hotbar',
    'Inventory',
    'PlayerState',
    'RecipeForNormal',
    'RecipeForFurnace',
    'RecipeForMulti',
    'RecipeData',
    'Recipe',
    'InventoryAction',
    'Block',
    'PlacedBlock',
]


PlayerID = UUID
EntityUniqueID = int
EntityRuntimeID = int

GameRule = NamedTuple('GameRule', [
    ('name', str),
    ('type', GameRuleType),
    ('value', Union[bool, int, float])
])

Attribute = NamedTuple('Attribute', [
    ('min', float),
    ('max', float),
    ('current', float),
    ('default', float),
    ('name', str)
])


class AdventureSettings(NamedTuple('AdventureSettings', [
    ('flags', int),
    ('flags2', int)
])):
    @staticmethod
    def create(**kwargs: bool) -> 'AdventureSettings':
        """
        >>> AdventureSettings.create(world_immutable=True, attack_players=True, flying=True, teleport=True)
        AdventureSettings(flags=513, flags2=136)
        """
        flags = dict_to_flags(AdventureSettingFlag1, **kwargs)
        flags2 = dict_to_flags(AdventureSettingFlag2, **kwargs)
        return AdventureSettings(flags, flags2)

    def to_dict(self) -> Dict[str, bool]:
        """
        >>> sorted(AdventureSettings(513, 136).to_dict().items())
        [('attack_players', True), ('flying', True), ('teleport', True), ('world_immutable', True)]
        """
        d = {}
        d.update(flags_to_dict(AdventureSettingFlag1, self.flags))
        d.update(flags_to_dict(AdventureSettingFlag2, self.flags2))
        return d


class Item(NamedTuple('Item', [
    ('type', ItemType),
    ('aux_value', Optional[int]),  # None if ItemType.AIR
    ('nbt', Optional[bytes]),  # None if ItemType.AIR
    ('place_on', Optional[Tuple[str, ...]]),  # None if ItemType.AIR
    ('destroy', Optional[Tuple[str, ...]])  # None if ItemType.AIR
])):
    __slots__ = ()

    @classmethod
    def create(
            cls,
            item_type: ItemType,
            quantity: int,
            item_data: int=0,
            nbt: bytes=b'',
            place_on: Tuple[str, ...]=(),
            destroy: Tuple[str, ...]=()
    ) -> 'Item':
        return Item(item_type, (item_data << 8) | quantity, nbt, place_on, destroy)

    @property
    def quantity(self) -> int:
        return self.aux_value & 0xff

    @property
    def data(self) -> int:
        return self.aux_value >> 8


MetaDataValue = Union[int, float, str, Vector3, Item]

EntityMetaData = NamedTuple('EntityMetaData', [
    ('key', EntityMetaDataKey),
    ('type', MetaDataType),
    ('value', MetaDataValue)
])


class EntityMetaDataFlagValue(NamedTuple('EntityMetaDataFlags', [
    ('flags', int)
])):
    @staticmethod
    def create(**kwargs: bool) -> 'EntityMetaDataFlagValue':
        """
        >>> EntityMetaDataFlagValue.create(always_show_nametag=True, immobile=True, swimmer=True)
        EntityMetaDataFlagValue(flags=1146880)
        """
        return EntityMetaDataFlagValue(dict_to_flags(EntityMetaDataFlag, **kwargs))

    def to_dict(self) -> Dict[str, bool]:
        """
        >>> sorted(EntityMetaDataFlagValue(1146880).to_dict().items())
        [('always_show_nametag', True), ('immobile', True), ('swimmer', True)]
        """
        return flags_to_dict(EntityMetaDataFlag, self.flags)


EntityAttribute = NamedTuple('EntityAttribute', [
    ('name', str),
    ('min', float),
    ('current', float),
    ('max', float)
])

EntityLink = NamedTuple('EntityLink', [
    ('from_entity_unique_id', EntityUniqueID),
    ('to_entity_unique_id', EntityUniqueID),
    ('type', int),
    ('bool1', bool)
])

Hotbar = Tuple[Optional[int], ...]

Inventory = NamedTuple('Inventory', [
    ('window_type', WindowType),
    ('slots', Tuple[Item, ...])
])

PlayerState = NamedTuple('PlayerState', [
    ('spawn_position', Vector3[int]),
    ('position', Vector3[float]),
    ('yaw', float),
    ('health', float),
    ('hunger', float),
    ('air', float),
    ('inventory', Inventory),
    ('armor', Inventory),
    ('hotbar', Hotbar)
])

RecipeForNormal = NamedTuple('RecipeForNormal', [
    ('width', Optional[int]),
    ('height', Optional[int]),
    ('input', Tuple[Item, ...]),
    ('output', Tuple[Item, ...]),
    ('uuid', UUID)
])

RecipeForFurnace = NamedTuple('RecipeForFurnace', [
    ('input_id', int),
    ('input_damage', Optional[int]),
    ('output', Item)
])

RecipeForMulti = NamedTuple('RecipeForMulti', [
    ('uuid', UUID)
])

RecipeData = Union[RecipeForNormal, RecipeForFurnace, RecipeForMulti]

Recipe = NamedTuple('Recipe', [
    ('type', RecipeType),
    ('data', RecipeData)
])

InventoryAction = NamedTuple('InventoryAction', [
    ('source_type', SourceType),
    ('window_type', Optional[WindowType]),
    ('unknown1', Optional[int]),
    ('inventory_slot', int),
    ('old_item', Item),
    ('new_item', Item)
])


class Block(NamedTuple('Block', [
    ('type', BlockType),
    ('aux_value', int)
])):
    def __str__(self) -> str:
        return '{}(type={}, data={}, flags={})'.format(self.__class__.__name__, self.type, self.data, self.flags)

    @staticmethod
    def create(block_type: BlockType, data: int, **flags: bool) -> 'Block':
        """
        >>> Block.create(BlockType.DIRT, 1, neighbors=True, network=True, priority=True)
        Block(type=<BlockType.DIRT: 3>, aux_value=177)
        """
        assert data <= 0xf
        return Block(block_type, dict_to_flags(BlockFlag, **flags) << 4 | data)

    @property
    def data(self) -> int:
        """
        >>> Block(BlockType.DIRT, 177).data
        1
        """
        return self.aux_value & 0xf

    @property
    def flags(self) -> Dict[str, bool]:
        """
        >>> sorted(Block(BlockType.DIRT, 177).flags.items())
        [('neighbors', True), ('network', True), ('priority', True)]
        """
        return flags_to_dict(BlockFlag, self.aux_value >> 4)

    def copy(self, block_type: Optional[BlockType]=None, data: Optional[int]=None, **flags: bool) -> 'Block':
        """
        >>> block = Block.create(BlockType.DIRT, 1, neighbors=True, network=True, priority=True)
        >>> block = block.copy(block_type=BlockType.GRASS, data=2, network=False)
        >>> block.type
        <BlockType.GRASS: 2>
        >>> block.data
        2
        >>> sorted(block.flags.items())
        [('neighbors', True), ('priority', True)]
        """
        block_type = self.type if block_type is None else block_type
        data = self.data if data is None else data
        new_flags = self.flags
        new_flags.update(flags)
        return Block.create(block_type, data, **new_flags)


PlacedBlock = NamedTuple('PlacedBlock', [
    ('position', Vector3[int]),
    ('block', Block)
])


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
