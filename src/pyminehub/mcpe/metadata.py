from pyminehub.mcpe.const import MetaDataType, EntityMetaDataKey
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.value import MetaDataValue, EntityMetaData, Slot


_ENTITY_META_DATA_TYPE = {
    EntityMetaDataKey.FLAGS: MetaDataType.LONG,
    EntityMetaDataKey.HEALTH: MetaDataType.INT,
    EntityMetaDataKey.VARIANT: MetaDataType.INT,
    EntityMetaDataKey.COLOR: MetaDataType.BYTE,
    EntityMetaDataKey.NAMETAG: MetaDataType.STRING,
    EntityMetaDataKey.OWNER_EID: MetaDataType.LONG,
    EntityMetaDataKey.TARGET_EID: MetaDataType.LONG,
    EntityMetaDataKey.AIR: MetaDataType.SHORT,
    EntityMetaDataKey.POTION_COLOR: MetaDataType.INT,
    EntityMetaDataKey.POTION_AMBIENT: MetaDataType.BYTE,
    EntityMetaDataKey.HURT_TIME: MetaDataType.INT,
    EntityMetaDataKey.HURT_DIRECTION: MetaDataType.INT,
    EntityMetaDataKey.PADDLE_TIME_LEFT: MetaDataType.FLOAT,
    EntityMetaDataKey.PADDLE_TIME_RIGHT: MetaDataType.FLOAT,
    EntityMetaDataKey.EXPERIENCE_VALUE: MetaDataType.INT,
    EntityMetaDataKey.MINECART_DISPLAY_BLOCK: MetaDataType.INT,
    EntityMetaDataKey.MINECART_DISPLAY_OFFSET: MetaDataType.INT,
    EntityMetaDataKey.MINECART_HAS_DISPLAY: MetaDataType.BYTE,
    EntityMetaDataKey.ENDERMAN_HELD_ITEM_ID: MetaDataType.SHORT,
    EntityMetaDataKey.ENDERMAN_HELD_ITEM_DAMAGE: MetaDataType.SHORT,
    EntityMetaDataKey.ENTITY_AGE: MetaDataType.SHORT,
    EntityMetaDataKey.BED_POSITION: MetaDataType.INT_VECTOR3,
    EntityMetaDataKey.FIREBALL_POWER_X: MetaDataType.FLOAT,
    EntityMetaDataKey.FIREBALL_POWER_Y: MetaDataType.FLOAT,
    EntityMetaDataKey.FIREBALL_POWER_Z: MetaDataType.FLOAT,
    EntityMetaDataKey.POTION_AUX_VALUE: MetaDataType.SHORT,
    EntityMetaDataKey.LEAD_HOLDER_EID: MetaDataType.LONG,
    EntityMetaDataKey.SCALE: MetaDataType.FLOAT,
    EntityMetaDataKey.INTERACTIVE_TAG: MetaDataType.STRING,
    EntityMetaDataKey.NPC_SKIN_ID: MetaDataType.STRING,
    EntityMetaDataKey.URL_TAG: MetaDataType.STRING,
    EntityMetaDataKey.MAX_AIR: MetaDataType.SHORT,
    EntityMetaDataKey.MARK_VARIANT: MetaDataType.INT,
    EntityMetaDataKey.BLOCK_TARGET: MetaDataType.INT_VECTOR3,
    EntityMetaDataKey.WITHER_INVULNERABLE_TICKS: MetaDataType.INT,
    EntityMetaDataKey.WITHER_TARGET_1: MetaDataType.LONG,
    EntityMetaDataKey.WITHER_TARGET_2: MetaDataType.LONG,
    EntityMetaDataKey.WITHER_TARGET_3: MetaDataType.LONG,
    EntityMetaDataKey.BOUNDING_BOX_WIDTH: MetaDataType.FLOAT,
    EntityMetaDataKey.BOUNDING_BOX_HEIGHT: MetaDataType.FLOAT,
    EntityMetaDataKey.FUSE_LENGTH: MetaDataType.INT,
    EntityMetaDataKey.RIDER_SEAT_POSITION: MetaDataType.FLOAT_VECTOR3,
    EntityMetaDataKey.RIDER_ROTATION_LOCKED: MetaDataType.BYTE,
    EntityMetaDataKey.RIDER_MAX_ROTATION: MetaDataType.FLOAT,
    EntityMetaDataKey.RIDER_MIN_ROTATION: MetaDataType.FLOAT,
    EntityMetaDataKey.AREA_EFFECT_CLOUD_RADIUS: MetaDataType.FLOAT,
    EntityMetaDataKey.AREA_EFFECT_CLOUD_WAITING: MetaDataType.INT,
    EntityMetaDataKey.AREA_EFFECT_CLOUD_PARTICLE_ID: MetaDataType.INT,
    EntityMetaDataKey.SHULKER_ATTACH_FACE: MetaDataType.BYTE,
    EntityMetaDataKey.SHULKER_ATTACH_POS: MetaDataType.INT_VECTOR3,
    EntityMetaDataKey.TRADING_PLAYER_EID: MetaDataType.LONG,
    EntityMetaDataKey.COMMAND_BLOCK_COMMAND: MetaDataType.STRING,
    EntityMetaDataKey.COMMAND_BLOCK_LAST_OUTPUT: MetaDataType.STRING,
    EntityMetaDataKey.COMMAND_BLOCK_TRACK_OUTPUT: MetaDataType.BYTE,
    EntityMetaDataKey.CONTROLLING_RIDER_SEAT_NUMBER: MetaDataType.BYTE,
    EntityMetaDataKey.STRENGTH: MetaDataType.INT,
    EntityMetaDataKey.MAX_STRENGTH: MetaDataType.INT
}


# noinspection PyTypeChecker
_TYPE_CHECKER = {
    MetaDataType.BYTE: lambda value: isinstance(value, int),
    MetaDataType.SHORT: lambda value: isinstance(value, int),
    MetaDataType.INT: lambda value: isinstance(value, int),
    MetaDataType.LONG: lambda value: isinstance(value, int),
    MetaDataType.FLOAT: lambda value: isinstance(value, float),
    MetaDataType.STRING: lambda value: isinstance(value, str),
    MetaDataType.SLOT: lambda value: isinstance(value, Slot),
    MetaDataType.INT_VECTOR3: lambda value: isinstance(value, Vector3) and all(isinstance(v, int) for v in value),
    MetaDataType.FLOAT_VECTOR3: lambda value: isinstance(value, Vector3) and all(isinstance(v, float) for v in value)
}


def create_entity_meta_data(key: EntityMetaDataKey, value: MetaDataValue) -> EntityMetaData:
    data_type = _ENTITY_META_DATA_TYPE[key]
    assert _TYPE_CHECKER[data_type](value)
    return EntityMetaData(key, data_type, value)
