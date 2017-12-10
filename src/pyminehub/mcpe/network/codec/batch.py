"""
Codecs for game packet in batch
"""
import base64
import json

from pyminehub.mcpe.network.codec.common import *
from pyminehub.mcpe.network.packet import *

_HEADER_EXTRA_DATA = RawData(2)

_LITTLE_ENDIAN_SHORT_DATA = ShortData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_INT_DATA = IntData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_LONG_DATA = LongData(endian=Endian.LITTLE)
_LITTLE_ENDIAN_FLOAT_DATA = FloatData(endian=Endian.LITTLE)

_LITTLE_ENDIAN_SIGNED_INT_DATA = IntData(endian=Endian.LITTLE, unsigned=False)

_VAR_INT_LENGTH_BYTES_DATA = BytesData(len_codec=VAR_INT_DATA)
_VAR_INT_LENGTH_STRING_DATA = StringData(len_codec=VAR_INT_DATA)


class _VarListData(DataCodec[Tuple[T, ...]]):

    def __init__(self, count_codec: DataCodec[int], item_codec: DataCodec[T]):
        self._count_codec = count_codec
        self._item_codec = item_codec

    def read(self, data: bytearray, context: DataCodecContext) -> Tuple[T, ...]:
        count = self._count_codec.read(data, context)
        return tuple(self._item_codec.read(data, context) for _ in range(count))

    def write(self, data: bytearray, value: Tuple[T, ...], context: DataCodecContext) -> None:
        self._count_codec.write(data, len(value), context)
        for entry in value:
            self._item_codec.write(data, entry, context)


TT = TypeVar('TT', bound=namedtuple)


class _CompositeData(DataCodec[TT]):

    def __init__(self, factory: Callable[..., TT], data_codecs: Tuple[DataCodec[Any], ...]):
        self._factory = factory
        self._data_codecs = data_codecs

    def read(self, data: bytearray, context: PacketCodecContext) -> TT:
        values = []
        context.stack.append(values)

        def generate():
            for data_codec in self._data_codecs:
                value = data_codec.read(data, context)
                values.append(value)
                yield value

        args = tuple(generate())
        context.stack.pop()
        return self._factory(*args)

    def write(self, data: bytearray, value: TT, context: PacketCodecContext) -> None:
        values = []
        context.stack.append(values)
        for v, data_codec in zip(value, self._data_codecs):
            data_codec.write(data, v, context)
            values.append(v)
        context.stack.pop()


_INT_VECTOR3_DATA = _CompositeData(Vector3, (
    VAR_INT_DATA,
    VAR_INT_DATA,
    VAR_INT_DATA
))

_FLOAT_VECTOR3_DATA = _CompositeData(Vector3, (
    _LITTLE_ENDIAN_FLOAT_DATA,
    _LITTLE_ENDIAN_FLOAT_DATA,
    _LITTLE_ENDIAN_FLOAT_DATA
))


ET = TypeVar('ET', bound=Enum)


class _EnumData(DataCodec[ET]):

    def __init__(self, data_codec: DataCodec[int], factory: Callable[[int], ET]):
        self._filter = ValueFilter(data_codec, read=lambda _data: factory(_data), write=lambda _value: _value.value)

    def read(self, data: bytearray, context: DataCodecContext) -> ET:
        return self._filter.read(data, context)

    def write(self, data: bytearray, value: ET, context: DataCodecContext):
        self._filter.write(data, value, context)


class _ConnectionRequest(DataCodec[ConnectionRequest]):

    BASE64_PADDING_BYTE = ord('=')

    @classmethod
    def _read_jwt(cls, data: bytes):
        head_base64, payload_base64, sig_base64 = data.split(b'.')
        padding = bytes(cls.BASE64_PADDING_BYTE for _ in range(len(payload_base64) % 4))
        return json.loads(base64.decodebytes(payload_base64 + padding))

    def read(self, data: bytearray, context: DataCodecContext) -> ConnectionRequest:
        length = VAR_INT_DATA.read(data, context)
        d = bytearray(pop_first(data, length))
        context.length += length

        local_context = DataCodecContext()
        chain_data = json.loads(pop_first(d, _LITTLE_ENDIAN_INT_DATA.read(d, local_context)))
        chain_list = tuple(map(lambda chain: self._read_jwt(bytes(chain, 'ascii')), chain_data['chain']))
        client_data_jwt = pop_first(d, _LITTLE_ENDIAN_INT_DATA.read(d, local_context))
        client_data = self._read_jwt(client_data_jwt)
        return ConnectionRequest(chain_list, client_data)

    def write(self, data: bytearray, value: ConnectionRequest, context: DataCodecContext) -> None:
        raise NotImplementedError()


_PACK_ENTRY_DATA = _VarListData(_LITTLE_ENDIAN_SHORT_DATA, _CompositeData(PackEntry, (
    STRING_DATA,
    STRING_DATA,
    _LITTLE_ENDIAN_LONG_DATA,
    STRING_DATA,
    STRING_DATA
)))

_PACK_STACK_DATA = _VarListData(VAR_INT_DATA, _CompositeData(PackStack, (
    STRING_DATA,
    STRING_DATA,
    STRING_DATA
)))


class _GameRule(DataCodec[GameRule]):

    _TYPE_MAP = {
        1: BOOL_DATA,
        2: VAR_INT_DATA,
        3: _LITTLE_ENDIAN_FLOAT_DATA
    }

    def read(self, data: bytearray, context: DataCodecContext) -> GameRule:
        rule_name = _VAR_INT_LENGTH_STRING_DATA.read(data, context)
        rule_type = VAR_INT_DATA.read(data, context)
        rule_value = self._TYPE_MAP[rule_type].read(data, context)
        return GameRule(rule_name, rule_type, rule_value)

    def write(self, data: bytearray, value: T, context: DataCodecContext) -> None:
        _VAR_INT_LENGTH_STRING_DATA.write(data, value.name, context)
        VAR_INT_DATA.write(data, value.type, context)
        self._TYPE_MAP[value.type].write(data, value.value, context)


class _CommandEnumIndex(DataCodec[int]):

    def read(self, data: bytearray, context: PacketCodecContext) -> int:
        enum_values_length = len(context.values[2])
        if enum_values_length < 256:
            return BYTE_DATA.read(data, context)
        elif enum_values_length < 65536:
            return _LITTLE_ENDIAN_SHORT_DATA.read(data, context)
        else:
            return _LITTLE_ENDIAN_INT_DATA.read(data, context)

    def write(self, data: bytearray, value: int, context: PacketCodecContext) -> None:
        enum_values_length = len(context.values[2])
        if enum_values_length < 256:
            BYTE_DATA.write(data, value, context)
        elif enum_values_length < 65536:
            _LITTLE_ENDIAN_SHORT_DATA.write(data, value, context)
        else:
            _LITTLE_ENDIAN_INT_DATA.write(data, value, context)


def _is_zero_first_value(_context: PacketCodecContext):
    return _context.stack[-1][0] == 0


_SLOT_DATA = _CompositeData(Slot, (
    VAR_INT_DATA,
    OptionalData(VAR_INT_DATA, _is_zero_first_value),
    OptionalData(BytesData(len_codec=_LITTLE_ENDIAN_SHORT_DATA), _is_zero_first_value),
    OptionalData(_VarListData(VAR_INT_DATA, _VAR_INT_LENGTH_STRING_DATA), _is_zero_first_value),
    OptionalData(_VarListData(VAR_INT_DATA, _VAR_INT_LENGTH_STRING_DATA), _is_zero_first_value)
))

_SLOTS = _VarListData(VAR_INT_DATA, _SLOT_DATA)


class _MetaDataValue(DataCodec[MetaDataValue]):

    _DATA_CODEC_MAP = {
        MetaDataType.BYTE: BYTE_DATA,
        MetaDataType.SHORT: _LITTLE_ENDIAN_SHORT_DATA,
        MetaDataType.INT: VAR_INT_DATA,
        MetaDataType.FLOAT: _LITTLE_ENDIAN_FLOAT_DATA,
        MetaDataType.STRING: _VAR_INT_LENGTH_STRING_DATA,
        MetaDataType.SLOT: _SLOT_DATA,
        MetaDataType.INT_VECTOR3: _INT_VECTOR3_DATA,
        MetaDataType.LONG: VAR_INT_DATA,
        MetaDataType.FLOAT_VECTOR3: _FLOAT_VECTOR3_DATA
    }

    def read(self, data: bytearray, context: PacketCodecContext) -> MetaDataValue:
        meta_data_type = context.stack[-1][1]
        return self._DATA_CODEC_MAP[meta_data_type].read(data, context)

    def write(self, data: bytearray, value: MetaDataValue, context: PacketCodecContext) -> None:
        meta_data_type = context.stack[-1][1]
        self._DATA_CODEC_MAP[meta_data_type].write(data, value, context)


_UUID_DATA = _CompositeData(UUID, (
    _LITTLE_ENDIAN_INT_DATA,
    _LITTLE_ENDIAN_INT_DATA,
    _LITTLE_ENDIAN_INT_DATA,
    _LITTLE_ENDIAN_INT_DATA
))


def _is_type_remove(context: PacketCodecContext) -> bool:
    return context.values[2] == PlayerListType.REMOVE


class _RecipeData(DataCodec[RecipeData]):

    def read(self, data: bytearray, context: PacketCodecContext) -> RecipeData:
        recipe_type = context.stack[-1][0]
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

    def write(self, data: bytearray, value: RecipeData, context: PacketCodecContext):
        recipe_type = context.stack[-1][0]
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


_game_data_codecs = {
    GamePacketID.LOGIN: [
        _HEADER_EXTRA_DATA,
        INT_DATA,
        _ConnectionRequest()
    ],
    GamePacketID.PLAY_STATUS: [
        _HEADER_EXTRA_DATA,
        _EnumData(INT_DATA, PlayStatus)
    ],
    GamePacketID.RESOURCE_PACKS_INFO: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _PACK_ENTRY_DATA,
        _PACK_ENTRY_DATA
    ],
    GamePacketID.RESOURCE_PACK_STACK: [
        _HEADER_EXTRA_DATA,
        BOOL_DATA,
        _PACK_STACK_DATA,
        _PACK_STACK_DATA
    ],
    GamePacketID.RESOURCE_PACK_CLIENT_RESPONSE: [
        _HEADER_EXTRA_DATA,
        _EnumData(BYTE_DATA, ResourcePackStatus),
        _VarListData(_LITTLE_ENDIAN_SHORT_DATA, STRING_DATA)
    ],
    GamePacketID.START_GAME: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _FLOAT_VECTOR3_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _EnumData(VAR_INT_DATA, Generator),
        VAR_INT_DATA,
        VAR_INT_DATA,
        _INT_VECTOR3_DATA,
        BOOL_DATA,
        VAR_INT_DATA,
        BOOL_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        _LITTLE_ENDIAN_FLOAT_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        _VarListData(VAR_INT_DATA, _GameRule()),
        BOOL_DATA,
        BOOL_DATA,
        BOOL_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        _VAR_INT_LENGTH_STRING_DATA,
        BOOL_DATA,
        _LITTLE_ENDIAN_LONG_DATA,
        VAR_INT_DATA
    ],
    GamePacketID.SET_TIME: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA
    ],
    GamePacketID.UPDATE_ATTRIBUTES: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        _VarListData(VAR_INT_DATA, _CompositeData(Attribute, (
            _LITTLE_ENDIAN_FLOAT_DATA,
            _LITTLE_ENDIAN_FLOAT_DATA,
            _LITTLE_ENDIAN_FLOAT_DATA,
            _LITTLE_ENDIAN_FLOAT_DATA,
            _VAR_INT_LENGTH_STRING_DATA
        )))
    ],
    GamePacketID.AVAILABLE_COMMANDS: [
        _HEADER_EXTRA_DATA,
        _VarListData(VAR_INT_DATA, _VAR_INT_LENGTH_STRING_DATA),
        _VarListData(VAR_INT_DATA, _VAR_INT_LENGTH_STRING_DATA),
        _VarListData(VAR_INT_DATA, _CompositeData(CommandEnum, (
            _VAR_INT_LENGTH_STRING_DATA,
            _VarListData(VAR_INT_DATA, _CommandEnumIndex())
        ))),
        _VarListData(VAR_INT_DATA, _CompositeData(CommandData, (
            _VAR_INT_LENGTH_STRING_DATA,
            _VAR_INT_LENGTH_STRING_DATA,
            BYTE_DATA,
            BYTE_DATA,
            _LITTLE_ENDIAN_SIGNED_INT_DATA,
            _VarListData(VAR_INT_DATA, _VarListData(VAR_INT_DATA, _CompositeData(CommandParameter, (
                _VAR_INT_LENGTH_STRING_DATA,
                _LITTLE_ENDIAN_SIGNED_INT_DATA,
                BOOL_DATA
            ))))
        )))
    ],
    GamePacketID.ADVENTURE_SETTINGS: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _LITTLE_ENDIAN_LONG_DATA
    ],
    GamePacketID.SET_ENTITY_DATA: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        _VarListData(VAR_INT_DATA, _CompositeData(EntityMetaData, (
            VAR_INT_DATA,
            _EnumData(VAR_INT_DATA, MetaDataType),
            _MetaDataValue()
        )))
    ],
    GamePacketID.INVENTORY_CONTENT: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        _VarListData(VAR_INT_DATA, _SLOT_DATA)
    ],
    GamePacketID.MOB_EQUIPMENT: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        _SLOT_DATA,
        BYTE_DATA,
        BYTE_DATA,
        BYTE_DATA
    ],
    GamePacketID.INVENTORY_SLOT: [
        _HEADER_EXTRA_DATA,
        VAR_INT_DATA,
        VAR_INT_DATA,
        _SLOT_DATA
    ],
    GamePacketID.PLAYER_LIST: [
        _HEADER_EXTRA_DATA,
        _EnumData(BYTE_DATA, PlayerListType),
        _VarListData(VAR_INT_DATA, _CompositeData(PlayerListEntry, (
            _UUID_DATA,
            OptionalData(VAR_INT_DATA, _is_type_remove),
            OptionalData(_VAR_INT_LENGTH_STRING_DATA, _is_type_remove),
            OptionalData(_CompositeData(Skin, (
                _VAR_INT_LENGTH_STRING_DATA,
                _VAR_INT_LENGTH_BYTES_DATA,
                _VAR_INT_LENGTH_STRING_DATA,
                _VAR_INT_LENGTH_STRING_DATA,
                _VAR_INT_LENGTH_STRING_DATA
            )), _is_type_remove),
            OptionalData(_VAR_INT_LENGTH_STRING_DATA, _is_type_remove)
        )))
    ],
    GamePacketID.CRAFTING_DATA: [
        _HEADER_EXTRA_DATA,
        _VarListData(VAR_INT_DATA, _CompositeData(Recipe, (
            _EnumData(VAR_SIGNED_INT_DATA, RecipeType),
            _RecipeData()
        ))),
        BOOL_DATA
    ],
    GamePacketID.REQUEST_CHUNK_RADIUS: [
        _HEADER_EXTRA_DATA,
        VAR_SIGNED_INT_DATA
    ]
}


game_packet_codec = Codec(GamePacketID, game_packet_factory, _game_data_codecs)
