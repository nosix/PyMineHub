import time
from logging import getLogger
from typing import Callable, Dict, List

from pyminehub.mcpe.const import PlayStatus, ResourcePackStatus, Dimension, Generator
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType, ConnectionPacket, connection_packet_factory
from pyminehub.mcpe.network.packet import EXTRA_DATA
from pyminehub.mcpe.network.packet import GamePacketType, GamePacket, game_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.player import Player
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import Reliability, GameDataHandler
from pyminehub.typevar import T

_logger = getLogger(__name__)


class PlayerSessionNotFound(Exception):
    pass


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = \
        (to_packet_format(('127.0.0.1', 0)),) + tuple(to_packet_format(('0.0.0.0', 0)) for _ in range(19))

    def __init__(self) -> None:
        self._start_time = time.time()
        self._ping_time = {}  # type: Dict[Address, int]
        self._accepted_time = {}  # type: Dict[Address, int]
        self._players = {}  # type: Dict[Address, Player]
        self._world = WorldProxy()
        self._queue = GamePacketQueue(self._send_connection_packet)

    def _get_current_time(self) -> int:
        """Get millisec time since starting handler."""
        return int(1000 * (time.time() - self._start_time))

    def data_received(self, data: bytes, addr: Address) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + ConnectionPacketType(packet.id).name.lower())(packet, addr)

    def _send_connection_packet(self, packet: ConnectionPacket, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: frame reliability
        """
        _logger.debug('< %s %s', addr, packet)
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    def _get_player_session(self, addr: Address) -> Player:
        if addr not in self._players:
            raise PlayerSessionNotFound(addr)
        return self._players[addr]

    def _foreach_players(self, action: Callable[[Player], T]) -> List[T]:
        return list(action(player) for player in self._players)

    def _process_connected_ping(self, packet: ConnectionPacket, addr: Address) -> None:
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PONG,
            packet.ping_time_since_start,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

    def _process_connected_pong(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.ping_time_since_start == self._ping_time[addr]:
            del self._ping_time[addr]

    def _process_connection_request(self, packet: ConnectionPacket, addr: Address) -> None:
        self._ping_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PING,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

        self._accepted_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
            to_packet_format(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr])
        self._send_connection_packet(res_packet, addr, Reliability(False, None))

    def _process_new_incoming_connection(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning('The packet of new incoming connection has invalid time. (expected:%d, actual: %d)',
                            self._accepted_time[addr], packet.server_time_since_start)
            return
        self._players[addr] = Player()

    def _process_batch(self, packet: ConnectionPacket, addr: Address) -> None:
        for data in packet.payloads:
            _logger.debug('%s [%d] %s', addr, len(data), data.hex())
            packet = game_packet_codec.decode(data)
            _logger.debug('> %s %s', addr, packet)
            try:
                getattr(self, '_process_' + GamePacketType(packet.id).name.lower())(packet, addr)
            except PlayerSessionNotFound as exc:
                _logger.info('{} player is not logged in.', exc)

    def _process_login(self, packet: GamePacket, addr: Address) -> None:
        player = self._get_player_session(addr)
        player_data = packet.connection_request.get_player_data()
        client_data = packet.connection_request.get_client_data()
        # TODO check the logged-in player and log out the same player
        player.login(packet.protocol, player_data, client_data)

        res_packet = game_packet_factory.create(GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self._queue.send_immediately(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: GamePacket, addr: Address) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:  # TODO does need?
            res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self._queue.send_immediately(res_packet, addr)
        self._start_game(addr)

    def _start_game(self, addr: Address) -> None:
        player = self._get_player_session(addr)
        res_packet = game_packet_factory.create(
            GamePacketType.START_GAME,
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
        res_packet = game_packet_factory.create(GamePacketType.SET_TIME, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.UPDATE_ATTRIBUTES, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.AVAILABLE_COMMANDS, )  # TODO s09
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.ADVENTURE_SETTINGS, )  # TODO 0s9
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.SET_ENTITY_DATA, )  # TODO s0a
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.INVENTORY_CONTENT, )  # TODO s0a, s0c
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.MOB_EQUIPMENT, )  # TODO s0d
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.INVENTORY_SLOT, )  # TODO s0d
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.PLAYER_LIST, )  # TODO s0f
        self._queue.send_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.CRAFTING_DATA, )  # TODO s20
        self._queue.send_immediately(res_packet, addr)
