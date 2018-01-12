import re
from typing import NamedTuple as _NamedTuple, Dict, Optional, Tuple, Union
from uuid import UUID

from pyminehub.binutil.converter import dict_to_flags, flags_to_dict, decode_base64
from pyminehub.mcpe.const import *
from pyminehub.mcpe.geometry import *

PlayerID = UUID
EntityUniqueID = int
EntityRuntimeID = int


Skin = _NamedTuple('Skin', [
    ('id', str),
    ('data', bytes),
    ('cape', str),
    ('geometry_name', str),
    ('geometry_data', str)
])

PlayerData = _NamedTuple('PlayerData', [
    ('xuid', str),
    ('identity', UUID),
    ('display_name', str),
    ('identity_public_key', str)
])


class ClientData(_NamedTuple('ClientData', [
    ('client_random_id', int),
    ('language_code', str),
    ('cape_data', str),
    ('skin_id', str),
    ('skin_data', bytes),
    ('skin_geometry_name', str),
    ('skin_geometry_data', str)
])):
    @property
    def skin(self) -> Skin:
        return Skin(self.skin_id, self.skin_data, self.cape_data, self.skin_geometry_name, self.skin_geometry_data)


class ConnectionRequest(_NamedTuple('ConnectionRequest', [
    ('chain', Tuple[dict, ...]),  # NOTE: dict is mutable
    ('client', dict)  # NOTE: dict is mutable
])):
    _KEY_EXTRA = 'extraData'
    _MINIMIZE_REGEXP = re.compile(r'\s+')

    @property
    def player_data(self) -> PlayerData:
        for webtoken in self.chain:
            if self._KEY_EXTRA in webtoken:
                extra_data = webtoken[self._KEY_EXTRA]
                identity = UUID('{' + extra_data['identity'] + '}')
                return PlayerData(
                    extra_data['XUID'], identity, extra_data['displayName'],
                    webtoken['identityPublicKey'])
        raise AssertionError('ConnectionRequest must have extraData.')

    @property
    def client_data(self) -> ClientData:
        skin_data = decode_base64(self.client['SkinData'].encode('ascii'))
        skin_geometry = decode_base64(self.client['SkinGeometry'].encode('ascii')).decode()
        return ClientData(
            self.client['ClientRandomId'],
            self.client['LanguageCode'],
            self.client['CapeData'],
            self.client['SkinId'],
            skin_data,
            self.client['SkinGeometryName'],
            self._MINIMIZE_REGEXP.sub('', skin_geometry).replace('.0', '')  # TODO remove replace '.0'
        )


PackEntry = _NamedTuple('PackEntry', [
    ('id', str),
    ('version', str),
    ('size', int),
    ('unknown1', str),
    ('unknown2', str)
])

PackStack = _NamedTuple('PackStack', [
    ('id', str),
    ('version', str),
    ('unknown1', str)
])

GameRule = _NamedTuple('GameRule', [
    ('name', str),
    ('type', GameRuleType),
    ('value', Union[bool, int, float])
])

Attribute = _NamedTuple('Attribute', [
    ('min', float),
    ('max', float),
    ('current', float),
    ('default', float),
    ('name', str)
])

CommandEnum = _NamedTuple('CommandEnum', [
    ('name', str),
    ('index', Tuple[int, ...])
])

CommandParameter = _NamedTuple('CommandParameter', [
    ('name', str),
    ('type', int),
    ('is_optional', bool)
])

CommandData = _NamedTuple('CommandData', [
    ('name', str),
    ('description', str),
    ('flags', int),
    ('permission', int),
    ('aliases', int),
    ('overloads', Tuple[Tuple[CommandParameter], ...])
])


class AdventureSettings(_NamedTuple('AdventureSettings', [
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


class Item(_NamedTuple('Item', [
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

EntityMetaData = _NamedTuple('EntityMetaData', [
    ('key', EntityMetaDataKey),
    ('type', MetaDataType),
    ('value', MetaDataValue)
])


class EntityMetaDataFlagValue(_NamedTuple('EntityMetaDataFlags', [
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


EntityAttribute = _NamedTuple('EntityAttribute', [
    ('name', str),
    ('min', float),
    ('current', float),
    ('max', float)
])

EntityLink = _NamedTuple('EntityLink', [
    ('from_entity_unique_id', EntityUniqueID),
    ('to_entity_unique_id', EntityUniqueID),
    ('type', int),
    ('bool1', bool)
])

Hotbar = Tuple[Optional[int], ...]

Inventory = _NamedTuple('Inventory', [
    ('window_type', WindowType),
    ('slots', Tuple[Item, ...])
])

PlayerState = _NamedTuple('PlayerState', [
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

PlayerListEntry = _NamedTuple('PlayerListEntry', [
    ('uuid', UUID),
    ('entity_unique_id', Optional[int]),
    ('user_name', Optional[str]),
    ('skin', Optional[Skin]),
    ('xbox_user_id', Optional[str])
])

RecipeForNormal = _NamedTuple('RecipeForNormal', [
    ('width', Optional[int]),
    ('height', Optional[int]),
    ('input', Tuple[Item, ...]),
    ('output', Tuple[Item, ...]),
    ('uuid', UUID)
])

RecipeForFurnace = _NamedTuple('RecipeForFurnace', [
    ('input_id', int),
    ('input_damage', Optional[int]),
    ('output', Item)
])

RecipeForMulti = _NamedTuple('RecipeForMulti', [
    ('uuid', UUID)
])

RecipeData = Union[RecipeForNormal, RecipeForFurnace, RecipeForMulti]

Recipe = _NamedTuple('Recipe', [
    ('type', RecipeType),
    ('data', RecipeData)
])

InventoryAction = _NamedTuple('InventoryAction', [
    ('source_type', SourceType),
    ('window_type', Optional[WindowType]),
    ('unknown1', Optional[int]),
    ('inventory_slot', int),
    ('old_item', Item),
    ('new_item', Item)
])

TransactionToUseItem = _NamedTuple('TransactionToUseItem', [
    ('action_type', UseItemActionType),
    ('position', Vector3[int]),
    ('face', Face),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('player_position', Vector3[float]),
    ('click_position', Vector3[float])
])

TransactionToUseItemOnEntity = _NamedTuple('TransactionToUseItemOnEntity', [
    ('entity_runtime_id', EntityRuntimeID),
    ('action_type', UseItemOnEntityActionType),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('unknown1', float),
    ('unknown2', float)
])

TransactionToReleaseItem = _NamedTuple('TransactionToReleaseItem', [
    ('action_type', ReleaseItemActionType),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('head_position', Vector3[float])
])

TransactionData = Union[TransactionToUseItem, TransactionToUseItemOnEntity, TransactionToReleaseItem]


class BlockData(_NamedTuple('BlockData', [
    ('value', int)
])):
    def __str__(self) -> str:
        return '{}(data={}, flags={})'.format(self.__class__.__name__, self.data, self.flags)

    @staticmethod
    def create(data: int, **kwargs: bool) -> 'BlockData':
        """
        >>> BlockData.create(1, neighbors=True, network=True, priority=True)
        BlockData(value=177)
        """
        assert data <= 0xf
        return BlockData(dict_to_flags(BlockFlag, **kwargs) << 4 | data)

    @property
    def data(self) -> int:
        """
        >>> BlockData(177).data
        1
        """
        return self.value & 0xf

    @property
    def flags(self) -> Dict[str, bool]:
        """
        >>> sorted(BlockData(177).flags.items())
        [('neighbors', True), ('network', True), ('priority', True)]
        """
        return flags_to_dict(BlockFlag, self.value >> 4)


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
