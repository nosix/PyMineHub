from pyminehub.mcpe.value import *
from pyminehub.network.address import AddressInPacket
from pyminehub.value import ValueType, ValueObject, ValueObjectFactory


ConnectionPacket = ValueObject
GamePacket = ValueObject


class ConnectionPacketType(ValueType):
    CONNECTED_PING = 0x00
    CONNECTED_PONG = 0x03
    CONNECTION_REQUEST = 0x09
    CONNECTION_REQUEST_ACCEPTED = 0x10
    NEW_INCOMING_CONNECTION = 0x13
    DISCONNECTION_NOTIFICATION = 0x15
    BATCH = 0xfe


class GamePacketType(ValueType):
    LOGIN = 0x01
    PLAY_STATUS = 0x02
    SERVER_TO_CLIENT_HANDSHAKE = 0x03
    CLIENT_TO_SERVER_HANDSHAKE = 0x04
    DISCONNECT = 0x05
    RESOURCE_PACKS_INFO = 0x06
    RESOURCE_PACK_STACK = 0x07
    RESOURCE_PACK_CLIENT_RESPONSE = 0x08
    TEXT = 0x09
    SET_TIME = 0x0a
    START_GAME = 0x0b
    ADD_PLAYER = 0x0c
    ADD_ENTITY = 0x0d
    REMOVE_ENTITY = 0x0e
    ADD_ITEM_ENTITY = 0x0f
    ADD_HANGING_ENTITY = 0x10
    TAKE_ITEM_ENTITY = 0x11
    MOVE_ENTITY = 0x12
    MOVE_PLAYER = 0x13
    RIDER_JUMP = 0x14
    UPDATE_BLOCK = 0x15
    ADD_PAINTING = 0x16
    EXPLODE = 0x17
    SOUND_EVENT = 0x18
    LEVEL_EVENT = 0x19
    BLOCK_EVENT = 0x1a
    ENTITY_EVENT = 0x1b
    MOB_EFFECT = 0x1c
    UPDATE_ATTRIBUTES = 0x1d
    INVENTORY_TRANSACTION = 0x1e
    MOB_EQUIPMENT = 0x1f
    MOB_ARMOR_EQUIPMENT = 0x20
    INTERACT = 0x21
    BLOCK_PICK_REQUEST = 0x22
    ENTITY_PICK_REQUEST = 0x23
    PLAYER_ACTION = 0x24
    ENTITY_FALL = 0x25
    HURT_ARMOR = 0x26
    SET_ENTITY_DATA = 0x27
    SET_ENTITY_MOTION = 0x28
    SET_ENTITY_LINK = 0x29
    SET_HEALTH = 0x2a
    SET_SPAWN_POSITION = 0x2b
    ANIMATE = 0x2c
    RESPAWN = 0x2d
    CONTAINER_OPEN = 0x2e
    CONTAINER_CLOSE = 0x2f
    PLAYER_HOTBAR = 0x30
    INVENTORY_CONTENT = 0x31
    INVENTORY_SLOT = 0x32
    CONTAINER_SET_DATA = 0x33
    CRAFTING_DATA = 0x34
    CRAFTING_EVENT = 0x35
    GUI_DATA_PICK_ITEM = 0x36
    ADVENTURE_SETTINGS = 0x37
    BLOCK_ENTITY_DATA = 0x38
    PLAYER_INPUT = 0x39
    FULL_CHUNK_DATA = 0x3a
    SET_COMMANDS_ENABLED = 0x3b
    SET_DIFFICULTY = 0x3c
    CHANGE_DIMENSION = 0x3d
    SET_PLAYER_GAME_TYPE = 0x3e
    PLAYER_LIST = 0x3f
    SIMPLE_EVENT = 0x40
    EVENT = 0x41
    SPAWN_EXPERIENCE_ORB = 0x42
    CLIENTBOUND_MAP_ITEM_DATA = 0x43
    MAP_INFO_REQUEST = 0x44
    REQUEST_CHUNK_RADIUS = 0x45
    CHUNK_RADIUS_UPDATED = 0x46
    ITEM_FRAME_DROP_ITEM = 0x47
    GAME_RULES_CHANGED = 0x48
    CAMERA = 0x49
    BOSS_EVENT = 0x4a
    SHOW_CREDITS = 0x4b
    AVAILABLE_COMMANDS = 0x4c
    COMMAND_REQUEST = 0x4d
    COMMAND_BLOCK_UPDATE = 0x4e
    COMMAND_OUTPUT = 0x4f
    UPDATE_TRADE = 0x50
    UPDATE_EQUIP = 0x51
    RESOURCE_PACK_DATA_INFO = 0x52
    RESOURCE_PACK_CHUNK_DATA = 0x53
    RESOURCE_PACK_CHUNK_REQUEST = 0x54
    TRANSFER = 0x55
    PLAY_SOUND = 0x56
    STOP_SOUND = 0x57
    SET_TITLE = 0x58
    ADD_BEHAVIOR_TREE = 0x59
    STRUCTURE_BLOCK_UPDATE = 0x5a
    SHOW_STORE_OFFER = 0x5b
    PURCHASE_RECEIPT = 0x5c
    PLAYER_SKIN = 0x5d
    SUB_CLIENT_LOGIN = 0x5e
    W_S_CONNECT = 0x5f
    SET_LAST_HURT_BY = 0x60
    BOOK_EDIT = 0x61
    NPC_REQUEST = 0x62
    PHOTO_TRANSFER = 0x63
    MODAL_FORM_REQUEST = 0x64
    MODAL_FORM_RESPONSE = 0x65
    SERVER_SETTINGS_REQUEST = 0x66
    SERVER_SETTINGS_RESPONSE = 0x67
    SHOW_PROFILE = 0x68
    SET_DEFAULT_GAME_TYPE = 0x69


_connection_packet_specs = {
    ConnectionPacketType.CONNECTED_PING: [
        ('id', int),
        ('ping_time_since_start', int)
    ],
    ConnectionPacketType.CONNECTED_PONG: [
        ('id', int),
        ('ping_time_since_start', int),
        ('pong_time_since_start', int)
    ],
    ConnectionPacketType.CONNECTION_REQUEST: [
        ('id', int),
        ('client_guid', int),
        ('client_time_since_start', int),
        ('use_encryption', bool)
    ],
    ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED: [
        ('id', int),
        ('client_address', AddressInPacket),
        ('system_index', int),
        ('internal_address', Tuple[AddressInPacket, ...]),
        ('client_time_since_start', int),
        ('server_time_since_start', int)
    ],
    ConnectionPacketType.NEW_INCOMING_CONNECTION: [
        ('id', int),
        ('server_address', AddressInPacket),
        ('internal_address', Tuple[AddressInPacket, ...]),
        ('server_time_since_start', int),
        ('client_time_since_start', int)
    ],
    ConnectionPacketType.DISCONNECTION_NOTIFICATION: [
        ('id', int)
    ],
    ConnectionPacketType.BATCH: [
        ('id', int),
        ('payloads', Tuple[bytes, ...])
    ]
}


_game_packet_specs = {
    GamePacketType.LOGIN: [
        ('id', int),
        ('extra', bytes),
        ('protocol', int),
        ('connection_request', ConnectionRequest)
    ],
    GamePacketType.PLAY_STATUS: [
        ('id', int),
        ('extra', bytes),
        ('status', PlayStatus)
    ],
    GamePacketType.RESOURCE_PACKS_INFO: [
        ('id', int),
        ('extra', bytes),
        ('must_accept', bool),
        ('behavior_pack_entries', Tuple[PackEntry, ...]),
        ('resource_pack_entries', Tuple[PackEntry, ...])
    ],
    GamePacketType.RESOURCE_PACK_STACK: [
        ('id', int),
        ('extra', bytes),
        ('must_accept', bool),
        ('behavior_pack_stack', Tuple[PackStack, ...]),
        ('resource_pack_stack', Tuple[PackStack, ...])
    ],
    GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE: [
        ('id', int),
        ('extra', bytes),
        ('status', ResourcePackStatus),
        ('pack_ids', Tuple[str, ...])
    ],
    GamePacketType.START_GAME: [
        ('id', int),
        ('extra', bytes),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('player_game_mode', GameMode),
        ('player_position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('seed', int),
        ('dimension', Dimension),
        ('generator', GeneratorType),
        ('world_game_mode', GameMode),
        ('difficulty', Difficulty),
        ('spawn', Vector3[int]),
        ('has_achievements_disabled', bool),
        ('time', int),
        ('edu_mode', bool),
        ('rain_level', float),
        ('lightning_level', float),
        ('is_multi_player_game', bool),
        ('has_lan_broadcast', bool),
        ('has_xbox_live_broadcast', bool),
        ('commands_enabled', bool),
        ('is_texture_packs_required', bool),
        ('game_rules', Tuple[GameRule, ...]),
        ('has_bonus_chest_enabled', bool),
        ('has_start_with_map_enabled', bool),
        ('has_trust_players_enabled', bool),
        ('default_player_permission', PlayerPermission),
        ('xbox_live_broadcast_mode', int),
        ('level_id', str),
        ('world_name', str),
        ('premium_world_template_id', str),
        ('unknown_bool', bool),
        ('current_tick', int),
        ('enchantment_seed', int)
    ],
    GamePacketType.SET_TIME: [
        ('id', int),
        ('extra', bytes),
        ('time', int)
    ],
    GamePacketType.UPDATE_ATTRIBUTES: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('entries', Tuple[Attribute, ...])
    ],
    GamePacketType.AVAILABLE_COMMANDS: [
        ('id', int),
        ('extra', bytes),
        ('enum_values', Tuple[str, ...]),
        ('postfixes', Tuple[str, ...]),
        ('enums', Tuple[CommandEnum, ...]),
        ('command_data', Tuple[CommandData, ...])
    ],
    GamePacketType.ADVENTURE_SETTINGS: [
        ('id', int),
        ('extra', bytes),
        ('flags', int),
        ('command_permission', CommandPermission),
        ('flags2', int),
        ('player_permission', PlayerPermission),
        ('custom_flags', int),
        ('entity_unique_id', EntityUniqueID)
    ],
    GamePacketType.SET_ENTITY_DATA: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', int),
        ('meta_data', Tuple[EntityMetaData, ...])
    ],
    GamePacketType.INVENTORY_CONTENT: [
        ('id', int),
        ('extra', bytes),
        ('window_id', WindowType),
        ('items', Union[Tuple[Slot, ...], bytes])  # bytes data is encoded items
    ],
    GamePacketType.MOB_EQUIPMENT: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('item', Slot),
        ('inventory_slot', int),
        ('hotbar_slot', int),
        ('window_id', WindowType)
    ],
    GamePacketType.INVENTORY_SLOT: [
        ('id', int),
        ('extra', bytes),
        ('window_id', WindowType),
        ('inventory_slot', int),
        ('item', Slot)
    ],
    GamePacketType.CRAFTING_DATA: [
        ('id', int),
        ('extra', bytes),
        ('recipe', Union[Tuple[Recipe, ...], bytes]),  # bytes data is encoded recipes
        ('clean_recipes', bool)
    ],
    GamePacketType.REQUEST_CHUNK_RADIUS: [
        ('id', int),
        ('extra', bytes),
        ('radius', int)
    ],
    GamePacketType.CHUNK_RADIUS_UPDATED: [
        ('id', int),
        ('extra', bytes),
        ('radius', int)
    ],
    GamePacketType.FULL_CHUNK_DATA: [
        ('id', int),
        ('extra', bytes),
        ('position', ChunkPosition),
        ('data', bytes)
    ],
    GamePacketType.PLAYER_LIST: [
        ('id', int),
        ('extra', bytes),
        ('type', PlayerListType),
        ('entries', Tuple[PlayerListEntry, ...])
    ],
    GamePacketType.ADD_PLAYER: [
        ('id', int),
        ('extra', bytes),
        ('uuid', UUID),
        ('user_name', str),
        ('entity_unique_id', EntityUniqueID),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('motion', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('item', Slot),
        ('metadata', EntityMetaData),
        ('unknown1', int),
        ('unknown2', int),
        ('unknown3', int),
        ('unknown4', int),
        ('unknown5', int),
        ('unknown_long', int),
        ('links', Tuple[EntityLink, ...])
    ],
    GamePacketType.REMOVE_ENTITY: [
        ('id', int),
        ('extra', bytes),
        ('entity_unique_id', EntityUniqueID)
    ],
    GamePacketType.DISCONNECT: [
        ('id', int),
        ('extra', bytes),
        ('hide_disconnection_screen', bool),
        ('message', str)
    ],
    GamePacketType.TEXT: [
        ('id', int),
        ('extra', bytes),
        ('type', TextType),
        ('needs_translation', bool),
        ('source', Optional[str]),
        ('message', str),
        ('parameters', Optional[Tuple[str, ...]]),
        ('xbox_user_id', str)
    ],
    GamePacketType.MOVE_PLAYER: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('yaw', float),
        ('head_yaw', float),
        ('mode', MoveMode),
        ('on_ground', bool),
        ('riding_eid', EntityRuntimeID),
        ('int1', Optional[int]),
        ('int2', Optional[int])
    ],
    GamePacketType.PLAYER_ACTION: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('action_type', PlayerActionType),
        ('position', Vector3[int]),
        ('face', int),
    ],
    GamePacketType.MOVE_ENTITY: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('position', Vector3[float]),
        ('pitch', float),
        ('head_yaw', float),
        ('yaw', float),
        ('on_ground', bool),
        ('teleported', bool)
    ],
    GamePacketType.ENTITY_EVENT: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('event_type', EntityEventType),
        ('data', int)
    ],
    GamePacketType.SET_ENTITY_MOTION: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('motion', Vector3[float])
    ],
    GamePacketType.SOUND_EVENT: [
        ('id', int),
        ('extra', bytes),
        ('sound', SoundType),
        ('position', Vector3[float]),
        ('extra_data', int),
        ('pitch', int),
        ('unknown', bool),
        ('disable_relative_volume', bool)
    ],
    GamePacketType.INTERACT: [
        ('id', int),
        ('extra', bytes),
        ('action_type', int),
        ('target', EntityRuntimeID),
        ('position', Vector3[float])
    ],
    GamePacketType.MOB_ARMOR_EQUIPMENT: [
        ('id', int),
        ('extra', bytes),
        ('entity_runtime_id', EntityRuntimeID),
        ('slots', Tuple[Slot, ...])
    ],
    GamePacketType.UPDATE_BLOCK: [
        ('id', int),
        ('extra', bytes),
        ('position', Vector3[int]),
        ('block_id', int),
        ('aux', int)
    ],
}


EXTRA_DATA = b'\x00\x00'

connection_packet_factory = ValueObjectFactory(_connection_packet_specs)
game_packet_factory = ValueObjectFactory(_game_packet_specs)
