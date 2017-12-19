import time
from logging import getLogger
from typing import Callable, Dict, List

from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.packet import ConnectionPacketType, ConnectionPacket, connection_packet_factory
from pyminehub.mcpe.network.packet import EXTRA_DATA
from pyminehub.mcpe.network.packet import GamePacketType, GamePacket, game_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.player import Player, PlayerID
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.mcpe.world.action import ActionType, action_factory
from pyminehub.mcpe.world.event import EventType, Event
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
        self._addrs = {}  # type: Dict[PlayerID, Address]
        self._world = WorldProxy()
        self._queue = GamePacketQueue(self._send_connection_packet)

    # GameDataHandler interface methods

    def data_received(self, data: bytes, addr: Address) -> None:
        _logger.debug('%s [%d] %s', addr, len(data), data.hex())
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s %s', addr, packet)
        getattr(self, '_process_' + ConnectionPacketType(packet.id).name.lower())(packet, addr)

    def update(self) -> bool:
        event = self._world.next_event()
        if event is None:
            return True
        _logger.debug('%s', event)
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

    def _foreach_players(self, action: Callable[[Player], T]) -> List[T]:
        return list(action(player) for player in self._players.values())

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
        self._addrs[player.get_id()] = addr

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

        player = self._get_player_session(addr)
        self._world.perform(action_factory.create(ActionType.LOGIN_PLAYER, player.get_id()))

    def _process_event_player_logged_in(self, event: Event) -> None:
        addr = self._get_addr(event.player_id)
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
            Generator.INFINITE,
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

        res_packet = game_packet_factory.create(
            GamePacketType.SET_TIME, EXTRA_DATA, 33868)  # TODO set time
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.UPDATE_ATTRIBUTES,
            EXTRA_DATA,
            player.get_entity_runtime_id(),
            (
                Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:health'),
                Attribute(0.0, 2048.0, 16.0, 16.0, 'minecraft:follow_range'),
                Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:knockback_resistance'),
                Attribute(0.0, 3.4028234663852886e+38, 0.10000000149011612, 0.10000000149011612, 'minecraft:movement'),
                Attribute(0.0, 3.4028234663852886e+38, 1.0, 1.0, 'minecraft:attack_damage'),
                Attribute(0.0, 3.4028234663852886e+38, 0.0, 0.0, 'minecraft:absorption'),
                Attribute(0.0, 20.0, 10.0, 20.0, 'minecraft:player.saturation'),
                Attribute(0.0, 5.0, 0.8000399470329285, 0.0, 'minecraft:player.exhaustion'),
                Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:player.hunger'),
                Attribute(0.0, 24791.0, 0.0, 0.0, 'minecraft:player.level'),
                Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:player.experience')
            )
        )
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.AVAILABLE_COMMANDS,
            EXTRA_DATA,
            enum_values=('suicide', 'pl', 'w', 'msg', 'ver', 'about'),
            postfixes=(),
            enums=(
                CommandEnum(name='KillAliases', index=(0,)),
                CommandEnum(name='PluginsAliases', index=(1,)),
                CommandEnum(name='TellAliases', index=(2, 3)),
                CommandEnum(name='VersionAliases', index=(4, 5))
            ),
            command_data=(
                CommandData(
                    name='ban',
                    description='Prevents the specified player from using this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),
                        ),
                    )
                ),
                CommandData(
                    name='ban-ip',
                    description='Prevents the specified IP address from using this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='banlist',
                    description='View all players banned from this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='defaultgamemode',
                    description='Set the default gamemode',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='deop',
                    description="Takes the specified player's operator status",
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='difficulty',
                    description='Sets the game difficulty',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='effect',
                    description='Adds/Removes effects on players',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='enchant',
                    description='Adds enchantments on items',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='gamemode',
                    description='Changes the player to a specific game mode',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='give',
                    description='Gives the specified player a certain amount of items',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='kick',
                    description='Removes the specified player from the server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='kill',
                    description='Commit suicide or kill other players',
                    flags=0, permission=0, aliases=0,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='list',
                    description='Lists all online players',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='me',
                    description='Performs the specified action in chat',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='op',
                    description='Gives the specified player operator status',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='pardon',
                    description='Allows the specified player to use this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='pardon-ip',
                    description='Allows the specified IP address to use this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='particle',
                    description='Adds particles to a world',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='plugins',
                    description='Gets a list of plugins running on the server',
                    flags=0, permission=0, aliases=1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='reload',
                    description='Reloads the server configuration and plugins',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='save-all',
                    description='Saves the server to disk',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='save-off',
                    description='Disables server autosaving',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='save-on',
                    description='Enables server autosaving',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='say',
                    description='Broadcasts the given message as the sender',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='seed',
                    description='Shows the world seed',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='setworldspawn',
                    description="Sets a worlds's spawn point. If no coordinates are specified, the player's coordinates will be used.",
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='spawnpoint',
                    description="Sets a player's spawn point",
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='stop',
                    description='Stops the server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='tp',
                    description='Teleports the given player (or yourself) to another player or coordinates',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='tell',
                    description='Sends a private message to the given player',
                    flags=0, permission=0, aliases=2,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='time',
                    description='Changes the time on each world',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='timings',
                    description='Records timings to see performance of the server.',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='title',
                    description='Controls screen titles',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='transferserver',
                    description='Transfer yourself to another server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='version',
                    description='Gets the version of this server including any plugins in use',
                    flags=0, permission=0, aliases=3,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ),
                CommandData(
                    name='whitelist',
                    description='Manages the list of players allowed to use this server',
                    flags=0, permission=0, aliases=-1,
                    overloads=(
                        (
                            CommandParameter(name='args', type=1048593, is_optional=True),),)
                ))
        )
        self._queue.send_immediately(res_packet, addr)

        res_packet = game_packet_factory.create(
            GamePacketType.ADVENTURE_SETTINGS,
            EXTRA_DATA,
            flags=32, command_permission=0, flags2=4294967295, player_permission=1, custom_flags=0, entity_unique_id=1
        )
        self._queue.send_immediately(res_packet, addr)

        # res_packet = game_packet_factory.create(GamePacketType.SET_ENTITY_DATA, )  # TODO s0a
        # self._queue.send_immediately(res_packet, addr)
        # res_packet = game_packet_factory.create(GamePacketType.INVENTORY_CONTENT, )  # TODO s0a, s0c
        # self._queue.send_immediately(res_packet, addr)
        # res_packet = game_packet_factory.create(GamePacketType.MOB_EQUIPMENT, )  # TODO s0d
        # self._queue.send_immediately(res_packet, addr)
        # res_packet = game_packet_factory.create(GamePacketType.INVENTORY_SLOT, )  # TODO s0d
        # self._queue.send_immediately(res_packet, addr)
        # res_packet = game_packet_factory.create(GamePacketType.PLAYER_LIST, )  # TODO s0f
        # self._queue.send_immediately(res_packet, addr)
        # res_packet = game_packet_factory.create(GamePacketType.CRAFTING_DATA, )  # TODO s20
        # self._queue.send_immediately(res_packet, addr)
