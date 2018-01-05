"""
Codecs for game packet in batch
"""
import json

from pyminehub.mcpe.network.packet import *
from pyminehub.network.codec import *

_HEADER_EXTRA_DATA = RawData(2)


_INT_VECTOR3_DATA = CompositeData(Vector3, (
    VAR_INT_DATA,
    VAR_INT_DATA,
    VAR_INT_DATA
))

_FLOAT_VECTOR3_DATA = CompositeData(Vector3, (
    L_FLOAT_DATA,
    L_FLOAT_DATA,
    L_FLOAT_DATA
))

_BLOCK_POSITION_DATA = CompositeData(Vector3, (
    VAR_SIGNED_INT_DATA,
    VAR_INT_DATA,
    VAR_SIGNED_INT_DATA
))


class _ConnectionRequest(DataCodec[ConnectionRequest]):

    @classmethod
    def _read_jwt(cls, data: bytes) -> str:
        head_base64, payload_base64, sig_base64 = data.split(b'.')
        return json.loads(decode_base64(payload_base64).decode())

    def read(self, data: bytearray, context: DataCodecContext) -> ConnectionRequest:
        length = VAR_INT_DATA.read(data, context)
        d = bytearray(pop_first(data, length))
        context.length += length

        local_context = DataCodecContext()
        chain_data_raw = pop_first(d, L_INT_DATA.read(d, local_context))
        chain_data = json.loads(chain_data_raw.decode())
        chain_list = tuple(map(lambda chain: self._read_jwt(chain.encode('ascii')), chain_data['chain']))
        client_data_jwt = pop_first(d, L_INT_DATA.read(d, local_context))
        client_data = self._read_jwt(client_data_jwt)
        return ConnectionRequest(chain_list, client_data)

    def write(self, data: bytearray, value: ConnectionRequest, context: DataCodecContext) -> None:
        raise NotImplementedError()


_PACK_ENTRY_DATA = VarListData(L_SHORT_DATA, CompositeData(PackEntry, (
    STRING_DATA,
    STRING_DATA,
    L_LONG_DATA,
    STRING_DATA,
    STRING_DATA
)))

_PACK_STACK_DATA = VarListData(VAR_INT_DATA, CompositeData(PackStack, (
    STRING_DATA,
    STRING_DATA,
    STRING_DATA
)))

_GAME_RULE_TYPE_DATA = EnumData(VAR_INT_DATA, GameRuleType)


class _GameRule(DataCodec[GameRule]):

    _VALUE_DATA_MAP = {
        GameRuleType.BOOL: BOOL_DATA,
        GameRuleType.INT: VAR_INT_DATA,
        GameRuleType.FLOAT: L_FLOAT_DATA
    }

    def read(self, data: bytearray, context: DataCodecContext) -> GameRule:
        rule_name = VAR_STRING_DATA.read(data, context)
        rule_type = _GAME_RULE_TYPE_DATA.read(data, context)
        rule_value = self._VALUE_DATA_MAP[rule_type].read(data, context)
        return GameRule(rule_name, rule_type, rule_value)

    def write(self, data: bytearray, value: GameRule, context: DataCodecContext) -> None:
        VAR_STRING_DATA.write(data, value.name, context)
        _GAME_RULE_TYPE_DATA.write(data, value.type, context)
        self._VALUE_DATA_MAP[value.type].write(data, value.value, context)


class _CommandEnumIndex(DataCodec[int]):

    def read(self, data: bytearray, context: CompositeCodecContext) -> int:
        enum_values_length = len(context['enum_values'])
        if enum_values_length < 256:
            return BYTE_DATA.read(data, context)
        elif enum_values_length < 65536:
            return L_SHORT_DATA.read(data, context)
        else:
            return L_INT_DATA.read(data, context)

    def write(self, data: bytearray, value: int, context: CompositeCodecContext) -> None:
        enum_values_length = len(context['enum_values'])
        if enum_values_length < 256:
            BYTE_DATA.write(data, value, context)
        elif enum_values_length < 65536:
            L_SHORT_DATA.write(data, value, context)
        else:
            L_INT_DATA.write(data, value, context)


def _is_zero_first_value(context: CompositeCodecContext):
    return context['slot_id'] == 0


_SLOT_DATA = CompositeData(Slot, (
    NamedData('slot_id', VAR_INT_DATA),
    OptionalData(VAR_INT_DATA, _is_zero_first_value),
    OptionalData(BytesData(len_codec=L_SHORT_DATA), _is_zero_first_value),
    OptionalData(VarListData(VAR_INT_DATA, VAR_STRING_DATA), _is_zero_first_value),
    OptionalData(VarListData(VAR_INT_DATA, VAR_STRING_DATA), _is_zero_first_value)
))

_SLOTS = VarListData(VAR_INT_DATA, _SLOT_DATA)  # type: DataCodec[Tuple[Slot, ...]]


class _InventoryContentItems(DataCodec[Tuple[Slot, ...]]):

    _CODEC = _SLOTS

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[Slot, ...]:
        return self._CODEC.read(data, context)

    def write(self, data: bytearray, value: Union[Tuple[Slot, ...], bytes], context: DataCodecContext) -> None:
        if isinstance(value, bytes):
            RAW_DATA.write(data, value, context)
        else:
            self._CODEC.write(data, value, context)


class _MetaDataValue(DataCodec[MetaDataValue]):

    _DATA_CODEC_MAP = {
        MetaDataType.BYTE: BYTE_DATA,
        MetaDataType.SHORT: L_SHORT_DATA,
        MetaDataType.INT: VAR_INT_DATA,
        MetaDataType.FLOAT: L_FLOAT_DATA,
        MetaDataType.STRING: VAR_STRING_DATA,
        MetaDataType.SLOT: _SLOT_DATA,
        MetaDataType.INT_VECTOR3: _INT_VECTOR3_DATA,
        MetaDataType.LONG: VAR_INT_DATA,
        MetaDataType.FLOAT_VECTOR3: _FLOAT_VECTOR3_DATA
    }

    def read(self, data: bytearray, context: CompositeCodecContext) -> MetaDataValue:
        metadata_type = context['metadata_type']
        return self._DATA_CODEC_MAP[metadata_type].read(data, context)

    def write(self, data: bytearray, value: MetaDataValue, context: CompositeCodecContext) -> None:
        metadata_type = context['metadata_type']
        self._DATA_CODEC_MAP[metadata_type].write(data, value, context)


_UUID_DATA = ValueFilter(RawData(16), read=lambda _data: UUID(bytes=_data), write=lambda _value: _value.bytes)


def _is_type_remove(context: CompositeCodecContext) -> bool:
    return context['player_list_type'] == PlayerListType.REMOVE


class _RecipeData(DataCodec[RecipeData]):

    def read(self, data: bytearray, context: CompositeCodecContext) -> RecipeData:
        recipe_type = context['recipe_type']
        if recipe_type in (RecipeType.SHAPED, RecipeType.SHAPELESS, RecipeType.SHULKER_BOX):
            width, height = None, None
            if recipe_type == RecipeType.SHAPED:
                width = VAR_SIGNED_INT_DATA.read(data, context)
                height = VAR_SIGNED_INT_DATA.read(data, context)
                input_slots = tuple(_SLOT_DATA.read(data, context) for _ in range(width * height))
            else:
                input_slots = _SLOTS.read(data, context)
            output_slots = _SLOTS.read(data, context)
            uuid = _UUID_DATA.read(data, context)
            return RecipeForNormal(width, height, input_slots, output_slots, uuid)
        if recipe_type in (RecipeType.FURNACE, RecipeType.FURNACE_DATA):
            input_id = VAR_SIGNED_INT_DATA.read(data, context)
            input_damage = VAR_SIGNED_INT_DATA.read(data, context) if recipe_type == RecipeType.FURNACE_DATA else None
            output_slot = _SLOT_DATA.read(data, context)
            return RecipeForFurnace(input_id, input_damage, output_slot)
        if recipe_type == RecipeType.MULTI:
            return RecipeForMulti(_UUID_DATA.read(data, context))

    def write(self, data: bytearray, value: RecipeData, context: CompositeCodecContext) -> None:
        recipe_type = context['recipe_type']
        if recipe_type in (RecipeType.SHAPED, RecipeType.SHAPELESS, RecipeType.SHULKER_BOX):
            if recipe_type == RecipeType.SHAPED:
                VAR_SIGNED_INT_DATA.write(data, value.width, context)
                VAR_SIGNED_INT_DATA.write(data, value.height, context)
                for slot in value.input:
                    _SLOT_DATA.write(data, slot, context)
            else:
                _SLOTS.write(data, value.input, context)
            _SLOTS.write(data, value.output, context)
            _UUID_DATA.write(data, value.uuid, context)
            return
        if recipe_type in (RecipeType.FURNACE, RecipeType.FURNACE_DATA):
            VAR_SIGNED_INT_DATA.write(data, value.input_id, context)
            if recipe_type == RecipeType.FURNACE_DATA:
                VAR_SIGNED_INT_DATA.write(data, value.input_damage, context)
            _SLOT_DATA.write(data, value.output, context)
            return
        if recipe_type == RecipeType.MULTI:
            _UUID_DATA.write(data, value.uuid, context)


class _RecipeList(DataCodec[Tuple[Recipe, ...]]):

    _CODEC = VarListData(VAR_INT_DATA, CompositeData(Recipe, (
        NamedData('recipe_type', EnumData(VAR_SIGNED_INT_DATA, RecipeType)),
        _RecipeData()
    )))  # type: DataCodec[Tuple[Recipe, ...]]

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[Recipe, ...]:
        return self._CODEC.read(data, context)

    def write(self, data: bytearray, value: Union[Tuple[Recipe, ...], bytes], context: DataCodecContext) -> None:
        if isinstance(value, bytes):
            RAW_DATA.write(data, value, context)
        else:
            self._CODEC.write(data, value, context)


_ENTITY_UNIQUE_ID = VAR_SIGNED_INT_DATA
_ENTITY_RUNTIME_ID = VAR_INT_DATA

_ENTITY_METADATA = VarListData(VAR_INT_DATA, CompositeData(EntityMetaData, (
    EnumData(VAR_INT_DATA, EntityMetaDataKey),
    NamedData('metadata_type', EnumData(VAR_INT_DATA, MetaDataType)),
    _MetaDataValue()
)))

_ENTITY_LINK = VarListData(VAR_INT_DATA, CompositeData(EntityLink, (
    _ENTITY_UNIQUE_ID,
    _ENTITY_UNIQUE_ID,
    BYTE_DATA,
    BOOL_DATA
)))

_CHUNK_POSITION = CompositeData(ChunkPosition, (
    VAR_SIGNED_INT_DATA,
    VAR_SIGNED_INT_DATA
))

_ANGLE_DATA = ValueFilter(BYTE_DATA, read=lambda _data: _data * (360 / 256), write=lambda _value: _value // (360 / 256))


class _TransactionData(DataCodec[Optional[TransactionData]]):

    _CODECS = {
        InventoryTransactionType.USE_ITEM: CompositeData(TransactionToUseItem, (
            VAR_INT_DATA,
            _BLOCK_POSITION_DATA,
            VAR_SIGNED_INT_DATA,
            VAR_SIGNED_INT_DATA,
            _SLOT_DATA,
            _FLOAT_VECTOR3_DATA,
            _FLOAT_VECTOR3_DATA
        )),
        InventoryTransactionType.USE_ITEM_ON_ENTITY: CompositeData(TransactionToUseItemOnEntity, (
            _ENTITY_RUNTIME_ID,
            VAR_INT_DATA,
            VAR_SIGNED_INT_DATA,
            _SLOT_DATA,
            _FLOAT_VECTOR3_DATA,
            _FLOAT_VECTOR3_DATA
        )),
        InventoryTransactionType.RELEASE_ITEM: CompositeData(TransactionToReleaseItem, (
            VAR_INT_DATA,
            VAR_SIGNED_INT_DATA,
            _SLOT_DATA,
            _FLOAT_VECTOR3_DATA
        ))
    }

    def read(self, data: bytearray, context: CompositeCodecContext) -> Optional[TransactionData]:
        try:
            return self._CODECS[context['transaction_type']].read(data, context)
        except KeyError:
            return None

    def write(self, data: bytearray, value: Optional[TransactionData], context: CompositeCodecContext) -> None:
        try:
            self._CODECS[context['transaction_type']].write(data, value, context)
        except KeyError:
            assert value is None


_game_data_codecs = {
    GamePacketType.LOGIN: [
        _HEADER_EXTRA_DATA,
        B_INT_DATA,
        _ConnectionRequest()
    ],
    GamePacketType.PLAY_STATUS: [
        _HEADER_EXTRA_DATA,
        EnumData(B_INT_DATA, PlayStatus)
    ],
    GamePacketType.RESOURCE_PACKS_INFO: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _PACK_ENTRY_DATA,
        _PACK_ENTRY_DATA
    ],
    GamePacketType.RESOURCE_PACK_STACK: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _PACK_STACK_DATA,
        _PACK_STACK_DATA
    ],
    GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE: [
        _HEADER_EXTRA_DATA,
        EnumData(BYTE_DATA, ResourcePackStatus),
        VarListData(L_SHORT_DATA, STRING_DATA)
    ],
    GamePacketType.START_GAME: [
        _HEADER_EXTRA_DATA,
        _ENTITY_UNIQUE_ID,
        _ENTITY_RUNTIME_ID,
        EnumData(VAR_SIGNED_INT_DATA, GameMode),
        _FLOAT_VECTOR3_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        VAR_SIGNED_INT_DATA,
        EnumData(VAR_SIGNED_INT_DATA, Dimension),
        EnumData(VAR_SIGNED_INT_DATA, GeneratorType),
        EnumData(VAR_SIGNED_INT_DATA, GameMode),
        EnumData(VAR_SIGNED_INT_DATA, Difficulty),
        _INT_VECTOR3_DATA,
        BOOL_DATA,
        VAR_SIGNED_INT_DATA,
        BOOL_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        VarListData(VAR_INT_DATA, _GameRule()),
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        EnumData(VAR_SIGNED_INT_DATA, PlayerPermission),
        VAR_SIGNED_INT_DATA,
        VAR_STRING_DATA,
        VAR_STRING_DATA,
        VAR_STRING_DATA,
        BOOL_DATA,
        L_LONG_DATA,
        VAR_SIGNED_INT_DATA
    ],
    GamePacketType.SET_TIME: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA
    ],
    GamePacketType.UPDATE_ATTRIBUTES: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        VarListData(VAR_INT_DATA, CompositeData(Attribute, (
            L_FLOAT_DATA,
            L_FLOAT_DATA,
            L_FLOAT_DATA,
            L_FLOAT_DATA,
            VAR_STRING_DATA
        )))
    ],
    GamePacketType.AVAILABLE_COMMANDS: [
        _HEADER_EXTRA_DATA,
        NamedData('enum_values', VarListData(VAR_INT_DATA, VAR_STRING_DATA)),
        VarListData(VAR_INT_DATA, VAR_STRING_DATA),
        VarListData(VAR_INT_DATA, CompositeData(CommandEnum, (
            VAR_STRING_DATA,
            VarListData(VAR_INT_DATA, _CommandEnumIndex())
        ))),
        VarListData(VAR_INT_DATA, CompositeData(CommandData, (
            VAR_STRING_DATA,
            VAR_STRING_DATA,
            BYTE_DATA,
            BYTE_DATA,
            L_SIGNED_INT_DATA,
            VarListData(VAR_INT_DATA, VarListData(VAR_INT_DATA, CompositeData(CommandParameter, (
                VAR_STRING_DATA,
                L_SIGNED_INT_DATA,
                BOOL_DATA
            ))))
        )))
    ],
    GamePacketType.ADVENTURE_SETTINGS: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        EnumData(VAR_INT_DATA, CommandPermission),
        VAR_INT_DATA,
        EnumData(VAR_INT_DATA, PlayerPermission),
        VAR_INT_DATA,
        L_LONG_DATA
    ],
    GamePacketType.SET_ENTITY_DATA: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        _ENTITY_METADATA
    ],
    GamePacketType.INVENTORY_CONTENT: [
        _HEADER_EXTRA_DATA,
        EnumData(VAR_INT_DATA, WindowType),
        _InventoryContentItems()
    ],
    GamePacketType.MOB_EQUIPMENT: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        _SLOT_DATA,
        BYTE_DATA,
        BYTE_DATA,
        EnumData(BYTE_DATA, WindowType)
    ],
    GamePacketType.INVENTORY_SLOT: [
        _HEADER_EXTRA_DATA,
        EnumData(VAR_INT_DATA, WindowType),
        VAR_INT_DATA,
        _SLOT_DATA
    ],
    GamePacketType.CRAFTING_DATA: [
        _HEADER_EXTRA_DATA,
        _RecipeList(),
        BOOL_DATA
    ],
    GamePacketType.REQUEST_CHUNK_RADIUS: [
        _HEADER_EXTRA_DATA,
        VAR_SIGNED_INT_DATA
    ],
    GamePacketType.CHUNK_RADIUS_UPDATED: [
        _HEADER_EXTRA_DATA,
        VAR_SIGNED_INT_DATA
    ],
    GamePacketType.FULL_CHUNK_DATA: [
        _HEADER_EXTRA_DATA,
        _CHUNK_POSITION,
        VAR_BYTES_DATA
    ],
    GamePacketType.PLAYER_LIST: [
        _HEADER_EXTRA_DATA,
        NamedData('player_list_type', EnumData(BYTE_DATA, PlayerListType)),
        VarListData(VAR_INT_DATA, CompositeData(PlayerListEntry, (
            _UUID_DATA,
            OptionalData(_ENTITY_UNIQUE_ID, _is_type_remove),
            OptionalData(VAR_STRING_DATA, _is_type_remove),
            OptionalData(CompositeData(Skin, (
                VAR_STRING_DATA,
                VAR_BYTES_DATA,
                VAR_STRING_DATA,
                VAR_STRING_DATA,
                VAR_STRING_DATA
            )), _is_type_remove),
            OptionalData(VAR_STRING_DATA, _is_type_remove)
        )))
    ],
    GamePacketType.ADD_PLAYER: [
        _HEADER_EXTRA_DATA,
        _UUID_DATA,
        VAR_STRING_DATA,
        _ENTITY_UNIQUE_ID,
        _ENTITY_RUNTIME_ID,
        _FLOAT_VECTOR3_DATA,
        _FLOAT_VECTOR3_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        _SLOT_DATA,
        _ENTITY_METADATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        L_LONG_DATA,
        _ENTITY_LINK
    ],
    GamePacketType.REMOVE_ENTITY: [
        _HEADER_EXTRA_DATA,
        _ENTITY_UNIQUE_ID
    ],
    GamePacketType.DISCONNECT: [
        _HEADER_EXTRA_DATA,
        NamedData('hide_screen', BOOL_DATA),
        OptionalData(VAR_STRING_DATA, lambda _context: _context['hide_screen'])
    ],
    GamePacketType.TEXT: [
        _HEADER_EXTRA_DATA,
        NamedData('text_type', EnumData(BYTE_DATA, TextType)),
        BOOL_DATA,
        OptionalData(VAR_STRING_DATA, lambda _context: not _context['text_type'].with_source),
        VAR_STRING_DATA,
        OptionalData(
            VarListData(VAR_INT_DATA, VAR_STRING_DATA),
            lambda _context: not _context['text_type'].with_parameters
        ),
        VAR_STRING_DATA
    ],
    GamePacketType.MOVE_PLAYER: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        _FLOAT_VECTOR3_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        NamedData('mode', EnumData(BYTE_DATA, MoveMode)),
        BOOL_DATA,
        _ENTITY_RUNTIME_ID,
        OptionalData(L_INT_DATA, lambda _context: _context['mode'] != MoveMode.TELEPORT),
        OptionalData(L_INT_DATA, lambda _context: _context['mode'] != MoveMode.TELEPORT),
    ],
    GamePacketType.PLAYER_ACTION: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        EnumData(VAR_INT_DATA, PlayerActionType),
        _INT_VECTOR3_DATA,
        VAR_INT_DATA
    ],
    GamePacketType.MOVE_ENTITY: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        _FLOAT_VECTOR3_DATA,
        _ANGLE_DATA,
        _ANGLE_DATA,
        _ANGLE_DATA,
        BOOL_DATA,
        BOOL_DATA
    ],
    GamePacketType.ENTITY_EVENT: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        EnumData(BYTE_DATA, EntityEventType),
        VAR_SIGNED_INT_DATA
    ],
    GamePacketType.SET_ENTITY_MOTION: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        _FLOAT_VECTOR3_DATA
    ],
    GamePacketType.SOUND_EVENT: [
        _HEADER_EXTRA_DATA,
        EnumData(BYTE_DATA, SoundType),
        _FLOAT_VECTOR3_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        BOOL_DATA,
        BOOL_DATA
    ],
    GamePacketType.INTERACT: [
        _HEADER_EXTRA_DATA,
        BYTE_DATA,
        _ENTITY_RUNTIME_ID,
        _FLOAT_VECTOR3_DATA
    ],
    GamePacketType.ANIMATE: [
        _HEADER_EXTRA_DATA,
        NamedData('action_type', VAR_INT_DATA),
        _ENTITY_RUNTIME_ID,
        OptionalData(L_FLOAT_DATA, lambda _context: not _context['action_type'] & 0x80)
    ],
    GamePacketType.INVENTORY_TRANSACTION: [
        _HEADER_EXTRA_DATA,
        NamedData('transaction_type', EnumData(VAR_INT_DATA, InventoryTransactionType)),
        VarListData(VAR_INT_DATA, CompositeData(InventoryAction, (
            NamedData('source_type', EnumData(VAR_INT_DATA, SourceType)),
            OptionalData(VAR_SIGNED_INT_DATA,
                         lambda _context: _context['source_type'] in (SourceType.WORLD, SourceType.CREATIVE)),
            OptionalData(VAR_INT_DATA,
                         lambda _context: _context['source_type'] != SourceType.WORLD),
            VAR_INT_DATA,
            _SLOT_DATA,
            _SLOT_DATA
        ))),
        _TransactionData()
    ],
    GamePacketType.ADD_ENTITY: [
        _HEADER_EXTRA_DATA,
        _ENTITY_UNIQUE_ID,
        _ENTITY_RUNTIME_ID,
        EnumData(VAR_INT_DATA, EntityType),
        _FLOAT_VECTOR3_DATA,
        _FLOAT_VECTOR3_DATA,
        L_FLOAT_DATA,
        L_FLOAT_DATA,
        VarListData(VAR_INT_DATA, CompositeData(EntityAttribute, (
            VAR_STRING_DATA,
            L_FLOAT_DATA,
            L_FLOAT_DATA,
            L_FLOAT_DATA
        ))),
        _ENTITY_METADATA,
        _ENTITY_LINK
    ],
    GamePacketType.MOB_ARMOR_EQUIPMENT: [
        _HEADER_EXTRA_DATA,
        _ENTITY_RUNTIME_ID,
        ListData(4, _SLOT_DATA)
    ],
    GamePacketType.SPACE_EVENT: [
        _HEADER_EXTRA_DATA,
        EnumData(VAR_SIGNED_INT_DATA, SpaceEventType),
        _FLOAT_VECTOR3_DATA,
        VAR_SIGNED_INT_DATA
    ],
    GamePacketType.UPDATE_BLOCK: [
        _HEADER_EXTRA_DATA,
        _BLOCK_POSITION_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA
    ],
}


game_packet_codec = PacketCodec(GamePacketType, game_packet_factory, _game_data_codecs)
