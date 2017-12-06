from enum import Enum
from typing import NamedTuple, Tuple

from pyminehub.network.address import Address
from pyminehub.network.packet import PacketFactory


class PacketID(Enum):
    connected_ping = 0x00
    connected_pong = 0x03
    connection_request = 0x09
    connection_request_accepted = 0x10
    new_incoming_connection = 0x13
    batch = 0xfe


class GamePacketID(Enum):
    login = 0x01
    play_status = 0x02
    server_to_client_handshake = 0x03
    client_to_server_handshake = 0x04
    disconnect = 0x05
    resource_packs_info = 0x06
    resource_pack_stack = 0x07
    resource_pack_client_response = 0x08
    text = 0x09
    set_time = 0x0a
    start_game = 0x0b
    add_player = 0x0c
    add_entity = 0x0d
    remove_entity = 0x0e
    add_item_entity = 0x0f
    add_hanging_entity = 0x10
    take_item_entity = 0x11
    move_entity = 0x12
    move_player = 0x13
    rider_jump = 0x14
    update_block = 0x15
    add_painting = 0x16
    explode = 0x17
    level_sound_event = 0x18
    level_event = 0x19
    block_event = 0x1a
    entity_event = 0x1b
    mob_effect = 0x1c
    update_attributes = 0x1d
    inventory_transaction = 0x1e
    mob_equipment = 0x1f
    mob_armor_equipment = 0x20
    interact = 0x21
    block_pick_request = 0x22
    entity_pick_request = 0x23
    player_action = 0x24
    entity_fall = 0x25
    hurt_armor = 0x26
    set_entity_data = 0x27
    set_entity_motion = 0x28
    set_entity_link = 0x29
    set_health = 0x2a
    set_spawn_position = 0x2b
    animate = 0x2c
    respawn = 0x2d
    container_open = 0x2e
    container_close = 0x2f
    player_hotbar = 0x30
    inventory_content = 0x31
    inventory_slot = 0x32
    container_set_data = 0x33
    crafting_data = 0x34
    crafting_event = 0x35
    gui_data_pick_item = 0x36
    adventure_settings = 0x37
    block_entity_data = 0x38
    player_input = 0x39
    full_chunk_data = 0x3a
    set_commands_enabled = 0x3b
    set_difficulty = 0x3c
    change_dimension = 0x3d
    set_player_game_type = 0x3e
    player_list = 0x3f
    simple_event = 0x40
    event = 0x41
    spawn_experience_orb = 0x42
    clientbound_map_item_data = 0x43
    map_info_request = 0x44
    request_chunk_radius = 0x45
    chunk_radius_updated = 0x46
    item_frame_drop_item = 0x47
    game_rules_changed = 0x48
    camera = 0x49
    boss_event = 0x4a
    show_credits = 0x4b
    available_commands = 0x4c
    command_request = 0x4d
    command_block_update = 0x4e
    command_output = 0x4f
    update_trade = 0x50
    update_equip = 0x51
    resource_pack_data_info = 0x52
    resource_pack_chunk_data = 0x53
    resource_pack_chunk_request = 0x54
    transfer = 0x55
    play_sound = 0x56
    stop_sound = 0x57
    set_title = 0x58
    add_behavior_tree = 0x59
    structure_block_update = 0x5a
    show_store_offer = 0x5b
    purchase_receipt = 0x5c
    player_skin = 0x5d
    sub_client_login = 0x5e
    w_s_connect = 0x5f
    set_last_hurt_by = 0x60
    book_edit = 0x61
    npc_request = 0x62
    photo_transfer = 0x63
    modal_form_request = 0x64
    modal_form_response = 0x65
    server_settings_request = 0x66
    server_settings_response = 0x67
    show_profile = 0x68
    set_default_game_type = 0x69


class ConnectionRequest(NamedTuple('ConnectionRequest', [('chain', Tuple[dict, ...]), ('client', dict)])):
    pass


class PlayStatus(Enum):
    login_success = 0
    login_failed_client = 1
    login_failed_server = 2
    player_spawn = 3
    login_failed_invalid_tenant = 4
    login_failed_vanilla_edu = 5
    login_failed_edu_vanilla = 6


PackEntry = NamedTuple('PackEntry', [('id', 'str'), ('version', 'str'), ('size', 'int')])


class ResourcePackStatus(Enum):
    refused = 1
    send_packs = 2
    have_all_packs = 3
    completed = 4

    
_packet_specs = {
    PacketID.connected_ping: [
        ('id', int),
        ('ping_time_since_start', int)
    ],
    PacketID.connected_pong: [
        ('id', int),
        ('ping_time_since_start', int),
        ('pong_time_since_start', int)
    ],
    PacketID.connection_request: [
        ('id', int),
        ('client_guid', int),
        ('client_time_since_start', int),
        ('use_encryption', bool)
    ],
    PacketID.connection_request_accepted: [
        ('id', int),
        ('client_address', Address),
        ('system_index', int),
        ('internal_address', Tuple[Address, ...]),
        ('client_time_since_start', int),
        ('server_time_since_start', int)
    ],
    PacketID.new_incoming_connection: [
        ('id', int),
        ('server_address', Address),
        ('internal_address', Tuple[Address, ...]),
        ('server_time_since_start', int),
        ('client_time_since_start', int)
    ],
    PacketID.batch: [
        ('id', int),
        ('payloads', Tuple[bytes, ...])
    ]
}


_game_packet_specs = {
    GamePacketID.login: [
        ('id', int),
        ('extra', bytes),
        ('protocol', int),
        ('connection_request', ConnectionRequest)
    ],
    GamePacketID.play_status: [
        ('id', int),
        ('extra', bytes),
        ('status', PlayStatus)
    ],
    GamePacketID.resource_packs_info: [
        ('id', int),
        ('extra', bytes),
        ('must_accept', bool),
        ('behavior_pack_entries', Tuple[PackEntry, ...]),
        ('resource_pack_entries', Tuple[PackEntry, ...])
    ],
    GamePacketID.resource_pack_client_response: [
        ('id', int),
        ('extra', bytes),
        ('status', ResourcePackStatus),
        ('pack_ids', Tuple[str, ...])
    ]
}


packet_factory = PacketFactory(_packet_specs)
game_packet_factory = PacketFactory(_game_packet_specs)
