import re
from typing import NamedTuple, Tuple, Optional, Union
from uuid import UUID

from pyminehub.binutil.converter import decode_base64
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.network.const import UseItemActionType, UseItemOnEntityActionType, ReleaseItemActionType
from pyminehub.mcpe.value import Item, EntityRuntimeID

__all__ = [
    'Skin',
    'PlayerData',
    'ClientData',
    'ConnectionRequest',
    'PackEntry',
    'PackStack',
    'PlayerListEntry',
    'TransactionToUseItem',
    'TransactionToUseItemOnEntity',
    'TransactionToReleaseItem',
    'TransactionData',
]


Skin = NamedTuple('Skin', [
    ('id', str),
    ('data', bytes),
    ('cape', str),
    ('geometry_name', str),
    ('geometry_data', str)
])

PlayerData = NamedTuple('PlayerData', [
    ('xuid', str),
    ('identity', UUID),
    ('display_name', str),
    ('identity_public_key', str)
])


class ClientData(NamedTuple('ClientData', [
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


class ConnectionRequest(NamedTuple('ConnectionRequest', [
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


PackEntry = NamedTuple('PackEntry', [
    ('id', str),
    ('version', str),
    ('size', int),
    ('unknown1', str),
    ('unknown2', str)
])

PackStack = NamedTuple('PackStack', [
    ('id', str),
    ('version', str),
    ('unknown1', str)
])

PlayerListEntry = NamedTuple('PlayerListEntry', [
    ('uuid', UUID),
    ('entity_unique_id', Optional[int]),
    ('user_name', Optional[str]),
    ('skin', Optional[Skin]),
    ('xbox_user_id', Optional[str])
])

TransactionToUseItem = NamedTuple('TransactionToUseItem', [
    ('action_type', UseItemActionType),
    ('position', Vector3[int]),
    ('face', Face),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('player_position', Vector3[float]),
    ('click_position', Vector3[float])
])

TransactionToUseItemOnEntity = NamedTuple('TransactionToUseItemOnEntity', [
    ('entity_runtime_id', EntityRuntimeID),
    ('action_type', UseItemOnEntityActionType),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('unknown1', float),
    ('unknown2', float)
])

TransactionToReleaseItem = NamedTuple('TransactionToReleaseItem', [
    ('action_type', ReleaseItemActionType),
    ('hotbar_slot', int),
    ('item_in_hand', Item),
    ('head_position', Vector3[float])
])

TransactionData = Union[TransactionToUseItem, TransactionToUseItemOnEntity, TransactionToReleaseItem]
