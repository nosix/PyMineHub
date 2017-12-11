import time
from collections import namedtuple
from logging import getLogger
from typing import Callable, List

from pyminehub.mcpe.const import PlayStatus, ResourcePackStatus, Dimension, Generator
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import EXTRA_DATA, ConnectionPacketID, connection_packet_factory
from pyminehub.mcpe.network.packet import GamePacketID, game_packet_factory
from pyminehub.mcpe.player import Player
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import to_address
from pyminehub.raknet import GameDataHandler
from pyminehub.typing import T

_logger = getLogger(__name__)


class PlayerSessionNotFound(Exception):
    pass


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = tuple(to_address(('0.0.0.0', 0)) for i in range(20))

    def __init__(self):
        self._start_time = time.time()
        self._accepted_time = {}
        self._players = {}
        self._world = WorldProxy()

    def _get_current_time(self):
        return int(time.time() - self._start_time)

    def data_received(self, data: bytes, addr: tuple) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + ConnectionPacketID(packet.id).name.lower())(packet, addr)

    def send_to_client(self, packet: namedtuple, addr: tuple) -> None:
        _logger.debug('< %s %s', addr, packet)
        self.sendto(connection_packet_codec.encode(packet), addr)

    def _get_player_session(self, addr: tuple) -> Player:
        if addr not in self._players:
            raise PlayerSessionNotFound(addr)
        return self._players[addr]

    def _foreach_players(self, action: Callable[[Player], T]) -> List[T]:
        return list(action(player) for player in self._players)

    def _process_connected_ping(self, packet: namedtuple, addr: tuple) -> None:
        res_packet = connection_packet_factory.create(
            ConnectionPacketID.CONNECTED_PONG,
            packet.ping_time_since_start,
            self._get_current_time())
        self.send_to_client(res_packet, addr)

    def _process_connection_request(self, packet: namedtuple, addr: tuple) -> None:
        self._accepted_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketID.CONNECTION_REQUEST_ACCEPTED,
            to_address(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr]
        )
        self.send_to_client(res_packet, addr)

    def _process_new_incoming_connection(self, packet: namedtuple, addr: tuple) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning('The packet of new incoming connection has invalid time. (expected:%d, actual: %d)',
                            self._accepted_time[addr], packet.server_time_since_start)
            return
        self._players[addr] = Player()

    def _process_batch(self, packet: namedtuple, addr: tuple) -> None:
        for data in packet.payloads:
            _logger.debug('%s [%d] %s', addr, len(data), data.hex())
            packet = game_packet_codec.decode(data)
            _logger.debug('> %s %s', addr, packet)
            try:
                getattr(self, '_process_' + GamePacketID(packet.id).name.lower())(packet, addr)
            except PlayerSessionNotFound as exc:
                _logger.info('{} player is not logged in.', exc)

    def _process_login(self, packet: namedtuple, addr: tuple) -> None:
        player = self._get_player_session(addr)
        player_data = packet.connection_request.get_player_data()
        client_data = packet.connection_request.get_client_data()
        # TODO check the logged-in player and log out the same player
        player.login(packet.protocol, player_data, client_data)

        res_packet = game_packet_factory.create(GamePacketID.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self.send_to_client(res_packet, addr)  # TODO encap batch
        res_packet = game_packet_factory.create(GamePacketID.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self.send_to_client(res_packet, addr)  # TODO encap batch

    def _process_resource_pack_client_response(self, packet: namedtuple, addr: tuple) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:  # TODO does need?
            res_packet = game_packet_factory.create(GamePacketID.RESOURCE_PACK_STACK, False, (), ())
            self.send_to_client(res_packet, addr)  # TODO encap batch
        self._start_game(addr)

    def _start_game(self, addr: tuple) -> None:
        player = self._get_player_session(addr)
        res_packet = game_packet_factory.create(
            GamePacketID.START_GAME,
            player.get_entity_unique_id(),
            player.get_entity_runtime_id(),
            player.get_game_mode(),
            player.get_position(),
            player.get_pitch(),
            player.get_yaw(),
            self._world.get_seed(),
            Dimension.OVERWORLD,
            Generator.FLAT,
            self._world.get_game_mode(),
            self._world.get_difficulty(),
            player.get_sapwn(),
            has_achievements_disabled=True,
            time=self._get_current_time(),
            edu_mode=False,
            rain_lavel=self._world.get_rain_level(),
            lighting_level=self._world.get_lightning_level(),
            is_multi_player_game=True,
            has_lan_broadcast=True,
            has_xbox_live_broadcast=False,
            commands_enabled=True,
            is_texture_packs_required=True,
            game_rules=(),
            has_bonus_chest_enabled=False,
            has_start_with_map_enabled=False,
            has_trust_players_enabled=False,
            default_player_permission=player.get_permission(),
            xbox_live_broadcast_mode=0,
            level_id='',
            world_name=self._world.get_world_name(),
            premium_world_template_id='',
            unknown_bool=False,
            current_tick=0,  # TODO set value
            enchantment_seed=0
        )
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.SET_TIME, )  # TODO s09
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.UPDATE_ATTRIBUTES, )  # TODO s09
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.AVAILABLE_COMMANDS, )  # TODO s09
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.ADVENTURE_SETTINGS, )  # TODO 0s9
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.SET_ENTITY_DATA, )  # TODO s0a
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.INVENTORY_CONTENT, )  # TODO s0a, s0c
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.MOB_EQUIPMENT, )  # TODO s0d
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.INVENTORY_SLOT, )  # TODO s0d
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.PLAYER_LIST, )  # TODO s0f
        self.send_to_client(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.CRAFTING_DATA, )  # TODO s20
        self.send_to_client(res_packet, addr)
