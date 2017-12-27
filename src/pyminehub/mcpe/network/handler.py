import time
from logging import getLogger

from pyminehub.mcpe.command import get_command_spec
from pyminehub.mcpe.metadata import create_entity_meta_data
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType, ConnectionPacket, connection_packet_factory
from pyminehub.mcpe.network.packet import EXTRA_DATA
from pyminehub.mcpe.network.packet import GamePacketType, GamePacket, game_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.network.reliability import UNRELIABLE
from pyminehub.mcpe.player import Player
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.mcpe.world.action import ActionType, action_factory
from pyminehub.mcpe.world.event import EventType, Event
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import Reliability, GameDataHandler

_logger = getLogger(__name__)


class PlayerSessionNotFound(Exception):
    pass


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = \
        (to_packet_format(('127.0.0.1', 0)),) + tuple(to_packet_format(('0.0.0.0', 0)) for _ in range(19))

    def __init__(self, world: WorldProxy) -> None:
        self._world = world
        self._start_time = time.time()
        self._ping_time = {}  # type: Dict[Address, int]
        self._accepted_time = {}  # type: Dict[Address, int]
        self._players = {}  # type: Dict[Address, Player]
        self._addrs = {}  # type: Dict[PlayerID, Address]
        self._queue = GamePacketQueue(self._send_connection_packet)
        # TODO world clock

    # GameDataHandler interface methods

    def data_received(self, data: bytes, addr: Address) -> None:
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + ConnectionPacketType(packet.id).name.lower())(packet, addr)

    def update(self) -> bool:
        event = self._world.next_event()
        if event is None:
            return True
        _logger.debug('EVENT:%s', event)
        try:
            getattr(self, '_process_event_' + EventType(event.id).name.lower())(event)
        except PlayerSessionNotFound as exc:
            _logger.info('Player is not logged in. (key=%s)', exc)
        return False

    # local methods

    def _get_current_time(self) -> int:
        """Get millisec time since starting handler."""
        return int(1000 * (time.time() - self._start_time))

    def _get_player_session(self, addr: Address) -> Player:
        if addr not in self._players:
            raise PlayerSessionNotFound(addr)
        return self._players[addr]

    def _get_addr(self, player_id: PlayerID) -> Address:
        if player_id not in self._addrs:
            raise PlayerSessionNotFound(player_id)
        return self._addrs[player_id]

    def _send_connection_packet(self, packet: ConnectionPacket, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: frame reliability
        """
        _logger.debug('< %s %s', addr, packet)
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    # packet and event handling methods

    def _process_connected_ping(self, packet: ConnectionPacket, addr: Address) -> None:
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PONG,
            packet.ping_time_since_start,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, UNRELIABLE)

    def _process_connected_pong(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.ping_time_since_start == self._ping_time[addr]:
            del self._ping_time[addr]

    def _process_connection_request(self, packet: ConnectionPacket, addr: Address) -> None:
        self._ping_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PING,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, UNRELIABLE)

        self._accepted_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
            to_packet_format(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr])
        self._send_connection_packet(res_packet, addr, UNRELIABLE)

    def _process_new_incoming_connection(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning('The packet of new incoming connection has invalid time. (expected:%d, actual: %d)',
                            self._accepted_time[addr], packet.server_time_since_start)
            return
        self._players[addr] = Player()

    def _process_batch(self, packet: ConnectionPacket, addr: Address) -> None:
        for data in packet.payloads:
            packet = game_packet_codec.decode(data)
            _logger.debug('> %s %s', addr, packet)
            try:
                getattr(self, '_process_' + GamePacketType(packet.id).name.lower())(packet, addr)
            except PlayerSessionNotFound as exc:
                _logger.info('Player is not logged in. (key=%s)', exc)

    def _process_login(self, packet: GamePacket, addr: Address) -> None:
        player = self._get_player_session(addr)
        player_data = packet.connection_request.player_data
        client_data = packet.connection_request.client_data
        # TODO check the logged-in player and log out the same player
        player.login(packet.protocol, player_data, client_data)
        self._addrs[player.id] = addr

        res_packet = game_packet_factory.create(GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self._queue.send_immediately(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: GamePacket, addr: Address) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:
            res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self._queue.send_immediately(res_packet, addr)
        elif packet.status == ResourcePackStatus.COMPLETED:
            player = self._get_player_session(addr)
            self._world.perform(action_factory.create(ActionType.LOGIN_PLAYER, player.id))

    def _process_request_chunk_radius(self, packet: GamePacket, addr: Address) -> None:
        player = self._get_player_session(addr)
        chunk_requests = player.get_required_chunk(packet.radius)
        self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, chunk_requests))
        res_packet = game_packet_factory.create(GamePacketType.CHUNK_RADIUS_UPDATED, EXTRA_DATA, packet.radius)
        self._queue.send_immediately(res_packet, addr)

    def _process_event_player_logged_in(self, event: Event) -> None:
        addr = self._get_addr(event.player_id)
        player = self._get_player_session(addr)

        player.entity_unique_id = event.entity_unique_id
        player.entity_runtime_id = event.entity_runtime_id
        player.position = event.position

        res_packet = game_packet_factory.create(
            GamePacketType.START_GAME,
            EXTRA_DATA,
            event.entity_unique_id,
            event.entity_runtime_id,
            event.game_mode,
            player.position,
            event.pitch,
            event.yaw,
            self._world.get_seed(),
            Dimension.OVERWORLD,
            Generator.INFINITE,
            self._world.get_game_mode(),
            self._world.get_difficulty(),
            event.spawn,
            has_achievements_disabled=True,
            time=self._world.get_time(),
            edu_mode=False,
            rain_level=self._world.get_rain_level(),
            lightning_level=self._world.get_lightning_level(),
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
            world_name=self._world.get_world_name(),
            premium_world_template_id='',
            unknown_bool=False,
            current_tick=0,  # TODO set value
            enchantment_seed=0
        )
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.SET_TIME, EXTRA_DATA, self._world.get_time())
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.UPDATE_ATTRIBUTES,
            EXTRA_DATA,
            player.entity_runtime_id,
            event.attributes
        )
        self._queue.send_immediately(res_packet, addr)

        command_spec = get_command_spec()

        res_packet = game_packet_factory.create(
            GamePacketType.AVAILABLE_COMMANDS,
            EXTRA_DATA,
            enum_values=command_spec.enum_values,
            postfixes=command_spec.postfixes,
            enums=command_spec.enums,
            command_data=command_spec.command_data
        )
        self._queue.send_immediately(res_packet, addr)

        adventure_settings = self._world.get_adventure_settings()

        res_packet = game_packet_factory.create(
            GamePacketType.ADVENTURE_SETTINGS,
            EXTRA_DATA,
            flags=adventure_settings.flags,
            command_permission=command_spec.permission,
            flags2=adventure_settings.flags2,
            player_permission=event.permission,
            custom_flags=0,
            entity_unique_id=event.entity_unique_id
        )
        self._queue.send_immediately(res_packet, addr)

        self._world.perform(action_factory.create(ActionType.UNKNOWN1, player.id))  # TODO remove

    def _process_event_unknown1(self, event: Event) -> None:
        addr = self._get_addr(event.player_id)
        player = self._get_player_session(addr)

        player.metadata_flags = event.flags

        res_packet = game_packet_factory.create(
            GamePacketType.SET_ENTITY_DATA,
            EXTRA_DATA,
            entity_runtime_id=player.entity_runtime_id,
            meta_data=(
                create_entity_meta_data(EntityMetaDataKey.FLAGS, player.metadata_flags.flags),
                create_entity_meta_data(EntityMetaDataKey.AIR, 0),
                create_entity_meta_data(EntityMetaDataKey.MAX_AIR, 400),
                create_entity_meta_data(EntityMetaDataKey.NAMETAG, player.name),
                create_entity_meta_data(EntityMetaDataKey.LEAD_HOLDER_EID, player.entity_runtime_id),  # TODO check
                create_entity_meta_data(EntityMetaDataKey.SCALE, 1.0),
                create_entity_meta_data(EntityMetaDataKey.BED_POSITION, event.bed_position)
            )
        )
        self._queue.send_immediately(res_packet, addr)

        for inventory in event.inventory:
            res_packet = game_packet_factory.create(
                GamePacketType.INVENTORY_CONTENT,
                EXTRA_DATA,
                window_id=inventory.window_type,
                items=inventory.slots
            )
            self._queue.send_immediately(res_packet, addr)

        self._world.perform(action_factory.create(ActionType.UNKNOWN2, player.id))  # TODO remove

    def _process_event_unknown2(self, event: Event) -> None:
        addr = self._get_addr(event.player_id)
        player = self._get_player_session(addr)

        res_packet = game_packet_factory.create(
            GamePacketType.MOB_EQUIPMENT,
            EXTRA_DATA,
            entity_runtime_id=player.entity_runtime_id,
            item=event.equipped_item,
            inventory_slot=event.inventory_slot,
            hotbar_slot=event.hotbar_slot,
            window_id=WindowType.INVENTORY
        )
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.INVENTORY_SLOT,
            EXTRA_DATA,
            window_id=WindowType.INVENTORY,
            inventory_slot=event.inventory_slot,
            item=event.equipped_item
        )
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.PLAYER_LIST,
            EXTRA_DATA,
            type=PlayerListType.ADD,
            entries=(
                PlayerListEntry(
                    uuid=player.uuid,
                    entity_unique_id=2,
                    user_name=player.name,
                    skin=player.skin,
                    xbox_user_id=''),))
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.CRAFTING_DATA,
            EXTRA_DATA,
            self._world.get_recipe(),
            True
        )
        self._queue.send_immediately(res_packet, addr)

    def _process_event_full_chunk_loaded(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.FULL_CHUNK_DATA, EXTRA_DATA, event.position, event.data)
        for addr, player in self._players.items():
            if player.did_request_chunk(event.position):
                self._queue.send_immediately(res_packet, addr)
                player.discard_chunk_request(event.position)
            self._spawn_player(player, addr)

    def _spawn_player(self, player: Player, addr: Address) -> None:
        if not player.is_living() and player.is_ready():
            res_packet = game_packet_factory.create(
                GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.PLAYER_SPAWN)
            self._queue.send_immediately(res_packet, addr)

            res_packet = game_packet_factory.create(
                GamePacketType.SET_ENTITY_DATA, EXTRA_DATA, player.entity_runtime_id, (
                    create_entity_meta_data(EntityMetaDataKey.FLAGS, player.metadata_flags.flags),
                    create_entity_meta_data(EntityMetaDataKey.NAMETAG, player.name)
                ))
            self._queue.send_immediately(res_packet, addr)

            player.sapwn()
