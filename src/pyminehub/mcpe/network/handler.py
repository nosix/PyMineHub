import time
from logging import getLogger
from typing import Callable, List

from pyminehub.mcpe.const import PlayStatus, ResourcePackStatus, Dimension, Generator
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import EXTRA_DATA, ConnectionPacketID, connection_packet_factory
from pyminehub.mcpe.network.packet import GamePacketID, game_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.player import Player
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address, to_packet_format
from pyminehub.network.packet import Packet
from pyminehub.raknet import Reliability, GameDataHandler
from pyminehub.typing import T

_logger = getLogger(__name__)


class PlayerSessionNotFound(Exception):
    pass


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = tuple(to_packet_format(('0.0.0.0', 0)) for i in range(20))

    def __init__(self) -> None:
        self._start_time = time.time()
        self._accepted_time = {}
        self._players = {}
        self._world = WorldProxy()
        self._queue = GamePacketQueue(self._send_connection_packet)

    def _get_current_time(self) -> int:
        return int(time.time() - self._start_time)

    def data_received(self, data: bytes, addr: Address) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + ConnectionPacketID(packet.id).name.lower())(packet, addr)

    def _send_connection_packet(self, packet: Packet, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: encapsulation reliability
        """
        _logger.debug('< %s %s', addr, packet)
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    def _get_player_session(self, addr: Address) -> Player:
        if addr not in self._players:
            raise PlayerSessionNotFound(addr)
        return self._players[addr]

    def _foreach_players(self, action: Callable[[Player], T]) -> List[T]:
        return list(action(player) for player in self._players)

    def _process_connected_ping(self, packet: Packet, addr: Address) -> None:
        res_packet = connection_packet_factory.create(
            ConnectionPacketID.CONNECTED_PONG,
            packet.ping_time_since_start,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

    def _process_connection_request(self, packet: Packet, addr: Address) -> None:
        self._accepted_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketID.CONNECTED_PING,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

        res_packet = connection_packet_factory.create(
            ConnectionPacketID.CONNECTION_REQUEST_ACCEPTED,
            to_packet_format(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr])
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

    def _process_new_incoming_connection(self, packet: Packet, addr: Address) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning('The packet of new incoming connection has invalid time. (expected:%d, actual: %d)',
                            self._accepted_time[addr], packet.server_time_since_start)
            return
        self._players[addr] = Player()

    def _process_batch(self, packet: Packet, addr: Address) -> None:
        for data in packet.payloads:
            _logger.debug('%s [%d] %s', addr, len(data), data.hex())
            packet = game_packet_codec.decode(data)
            _logger.debug('> %s %s', addr, packet)
            try:
                getattr(self, '_process_' + GamePacketID(packet.id).name.lower())(packet, addr)
            except PlayerSessionNotFound as exc:
                _logger.info('{} player is not logged in.', exc)

    def _process_login(self, packet: Packet, addr: Address) -> None:
        player = self._get_player_session(addr)
        player_data = packet.connection_request.get_player_data()
        client_data = packet.connection_request.get_client_data()
        # TODO check the logged-in player and log out the same player
        player.login(packet.protocol, player_data, client_data)

        res_packet = game_packet_factory.create(GamePacketID.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self._queue.send_immediately(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: Packet, addr: Address) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:  # TODO does need?
            res_packet = game_packet_factory.create(GamePacketID.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self._queue.send_immediately(res_packet, addr)
        self._start_game(addr)

    def _start_game(self, addr: Address) -> None:
        player = self._get_player_session(addr)
        res_packet = game_packet_factory.create(
            GamePacketID.START_GAME,
            EXTRA_DATA,
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
            default_player_permission=player.get_permission(),
            xbox_live_broadcast_mode=0,
            level_id='',
            world_name=self._world.get_world_name(),
            premium_world_template_id='',
            unknown_bool=False,
            current_tick=0,  # TODO set value
            enchantment_seed=0
        )
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.SET_TIME, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.UPDATE_ATTRIBUTES, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.AVAILABLE_COMMANDS, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.ADVENTURE_SETTINGS, )  # TODO 0s9
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.SET_ENTITY_DATA, )  # TODO s0a
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.INVENTORY_CONTENT, )  # TODO s0a, s0c
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.MOB_EQUIPMENT, )  # TODO s0d
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.INVENTORY_SLOT, )  # TODO s0d
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.PLAYER_LIST, )  # TODO s0f
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketID.CRAFTING_DATA, )  # TODO s20
        self._queue.send_immediately(res_packet, addr)
