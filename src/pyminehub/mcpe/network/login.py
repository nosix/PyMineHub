from typing import Callable

from pyminehub.mcpe.command import CommandRegistry
from pyminehub.mcpe.event import EventType
from pyminehub.mcpe.metadata import create_entity_metadata
from pyminehub.mcpe.network.packet import *
from pyminehub.mcpe.network.player import Player
from pyminehub.mcpe.network.session import SessionManager
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address


def login_sequence(
        player: Player,
        addr: Address,
        session: SessionManager,
        world: WorldProxy,
        command: CommandRegistry,
        send: Callable[[GamePacket, Address], None]
):
    event = yield
    assert event.type == EventType.PLAYER_LOGGED_IN

    player.set_identity(event.entity_unique_id, event.entity_runtime_id)
    player.position = event.position
    player.yaw = event.yaw

    player.metadata = (
        create_entity_metadata(EntityMetaDataKey.FLAGS, event.metadata_flags.flags),
        create_entity_metadata(EntityMetaDataKey.AIR, 0),
        create_entity_metadata(EntityMetaDataKey.MAX_AIR, 400),
        create_entity_metadata(EntityMetaDataKey.NAMETAG, player.name),
        create_entity_metadata(EntityMetaDataKey.LEAD_HOLDER_EID, 1),  # TODO check that it is always 1
        create_entity_metadata(EntityMetaDataKey.SCALE, 1.0),
        create_entity_metadata(EntityMetaDataKey.BED_POSITION, event.bed_position)
    )

    res_packet = game_packet_factory.create(
        GamePacketType.START_GAME,
        EXTRA_DATA,
        player.entity_unique_id,
        player.entity_runtime_id,
        event.game_mode,
        player.position,
        event.pitch,
        event.yaw,
        world.get_seed(),
        Dimension.OVERWORLD,
        GeneratorType.INFINITE,
        world.get_game_mode(),
        world.get_difficulty(),
        event.spawn,
        has_achievements_disabled=True,
        time=world.get_time(),
        edu_mode=False,
        rain_level=world.get_rain_level(),
        lightning_level=world.get_lightning_level(),
        is_multi_player_game=True,
        has_lan_broadcast=True,
        has_xbox_live_broadcast=False,
        commands_enabled=True,
        is_texture_packs_required=True,
        game_rules=(),
        has_bonus_chest_enabled=False,
        has_start_with_map_enabled=False,
        has_trust_players_enabled=False,
        default_player_permission=event.permission,
        xbox_live_broadcast_mode=0,
        level_id='',
        world_name=world.get_world_name(),
        premium_world_template_id='',
        unknown_bool=False,
        current_tick=0,  # TODO set value
        enchantment_seed=0
    )
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.SET_TIME, EXTRA_DATA, world.get_time())
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.UPDATE_ATTRIBUTES,
        EXTRA_DATA,
        player.entity_runtime_id,
        event.attributes
    )
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.SET_ENTITY_DATA,
        EXTRA_DATA,
        entity_runtime_id=player.entity_runtime_id,
        metadata=player.metadata
    )
    send(res_packet, addr)

    command_spec = command.get_command_spec()

    res_packet = game_packet_factory.create(
        GamePacketType.AVAILABLE_COMMANDS,
        EXTRA_DATA,
        enum_values=command_spec.enum_values,
        postfixes=command_spec.postfixes,
        enums=command_spec.enums,
        command_data=command_spec.command_data
    )
    send(res_packet, addr)

    adventure_settings = world.get_adventure_settings()

    res_packet = game_packet_factory.create(
        GamePacketType.ADVENTURE_SETTINGS,
        EXTRA_DATA,
        flags=adventure_settings.flags,
        command_permission=command_spec.permission,
        flags2=adventure_settings.flags2,
        player_permission=event.permission,
        custom_flags=0,
        entity_unique_id=player.entity_unique_id
    )
    send(res_packet, addr)

    event = yield
    assert event.type == EventType.INVENTORY_LOADED

    for inventory in event.inventory:
        res_packet = game_packet_factory.create(
            GamePacketType.INVENTORY_CONTENT,
            EXTRA_DATA,
            window_type=inventory.window_type,
            items=inventory.slots
        )
        send(res_packet, addr)

    event = yield
    assert event.type == EventType.SLOT_INITIALIZED

    player.equipped_item = event.equipped_item
    inventory_slot = event.inventory_slot if event.inventory_slot is not None else 0

    res_packet = game_packet_factory.create(
        GamePacketType.MOB_EQUIPMENT,
        EXTRA_DATA,
        entity_runtime_id=player.entity_runtime_id,
        item=event.equipped_item,
        inventory_slot=inventory_slot,
        hotbar_slot=event.hotbar_slot,
        window_type=WindowType.INVENTORY
    )
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.INVENTORY_SLOT,
        EXTRA_DATA,
        window_type=WindowType.INVENTORY,
        inventory_slot=inventory_slot,
        item=event.equipped_item
    )
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.CRAFTING_DATA,
        EXTRA_DATA,
        world.get_recipe(),
        True
    )
    send(res_packet, addr)

    res_packet = game_packet_factory.create(
        GamePacketType.PLAYER_LIST,
        EXTRA_DATA,
        list_type=PlayerListType.ADD,
        entries=tuple(
            PlayerListEntry(
                uuid=p.id,
                entity_unique_id=p.entity_unique_id,
                user_name=p.name,
                skin=p.skin,
                xbox_user_id='')
            for _, p in session.excluding(player)))
    send(res_packet, addr)

    _notify_new_player(player, session, send)

    while not player.is_ready():
        event = yield
        assert event.type == EventType.FULL_CHUNK_LOADED

    _spawn_player(player, addr, session, send)


def _notify_new_player(
        player: Player,
        session: SessionManager,
        send: Callable[[GamePacket, Address], None]
) -> None:
    assert player.has_identity()

    if player.invisible:
        return

    res_packet = game_packet_factory.create(
        GamePacketType.PLAYER_LIST,
        EXTRA_DATA,
        list_type=PlayerListType.ADD,
        entries=(
            PlayerListEntry(
                uuid=player.id,
                entity_unique_id=player.entity_unique_id,
                user_name=player.name,
                skin=player.skin,
                xbox_user_id=''),
        )
    )
    for addr, p in session.excluding(player):
        send(res_packet, addr)


def _spawn_player(
        player: Player,
        addr: Address,
        session: SessionManager,
        send: Callable[[GamePacket, Address], None]
) -> None:
    res_packet = game_packet_factory.create(
        GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.PLAYER_SPAWN)
    send(res_packet, addr)

    if player.invisible:
        return

    text_packet = game_packet_factory.create(
        GamePacketType.TEXT,
        EXTRA_DATA,
        TextType.TRANSLATION,
        False,
        None,
        EscapeSequence.YELLOW.value + '%multiplayer.player.joined',
        (player.name, ),
        ''
    )

    for other_player_addr, p in session:
        send(text_packet, other_player_addr)

    new_player_packet = game_packet_factory.create(
        GamePacketType.ADD_PLAYER,
        EXTRA_DATA,
        player.id,
        player.name,
        player.entity_unique_id,
        player.entity_runtime_id,
        player.bottom_position,
        Vector3(0.0, 0.0, 0.0),
        0.0, player.yaw, 0.0,
        player.equipped_item,
        player.metadata,
        0, 0, 0, 0, 0,
        0,
        tuple()
    )

    for other_player_addr, p in session.excluding(player):
        send(new_player_packet, other_player_addr)

        other_player_packet = game_packet_factory.create(
            GamePacketType.ADD_PLAYER,
            EXTRA_DATA,
            p.id,
            p.name,
            p.entity_unique_id,
            p.entity_runtime_id,
            p.bottom_position,
            Vector3(0.0, 0.0, 0.0),
            0.0, p.yaw, 0.0,
            p.equipped_item,
            p.metadata,
            0, 0, 0, 0, 0,
            0,
            tuple()
        )
        send(other_player_packet, addr)
