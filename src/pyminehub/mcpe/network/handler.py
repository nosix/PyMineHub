import time
from logging import getLogger

from pyminehub.mcpe.action import ActionType, action_factory
from pyminehub.mcpe.event import EventType, Event
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.login import login_sequence
from pyminehub.mcpe.network.packet import ConnectionPacketType, ConnectionPacket, connection_packet_factory
from pyminehub.mcpe.network.packet import EXTRA_DATA
from pyminehub.mcpe.network.packet import GamePacketType, GamePacket, game_packet_factory
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.network.reliability import UNRELIABLE, DEFAULT_CHANEL
from pyminehub.mcpe.network.session import SessionManager
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address, get_unspecified_address, to_packet_format
from pyminehub.raknet import Reliability, SessionNotFound, GameDataHandler
from pyminehub.value import LogString

_logger = getLogger(__name__)


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = tuple(to_packet_format((get_unspecified_address(), 0)) for _ in range(20))

    def __init__(self, world: WorldProxy) -> None:
        self._world = world
        self._start_time = time.time()
        self._ping_time = {}  # type: Dict[Address, int]
        self._accepted_time = {}  # type: Dict[Address, int]
        self._session_manager = SessionManager()
        self._queue = GamePacketQueue(self._send_connection_packet)
        # TODO world clock

    # GameDataHandler interface methods

    def data_received(self, data: bytes, addr: Address) -> None:
        packet = connection_packet_codec.decode(data)
        _logger.debug('> %s', LogString(packet))
        getattr(self, '_process_' + ConnectionPacketType(packet.id).name.lower())(packet, addr)

    async def update(self) -> None:
        event = await self._world.next_event()
        getattr(self, '_process_event_' + EventType(event.id).name.lower())(event)

    def terminate(self) -> None:
        res_packet = connection_packet_factory.create(ConnectionPacketType.DISCONNECTION_NOTIFICATION)
        for addr in self._session_manager.addresses:
            self._send_connection_packet(res_packet, addr, DEFAULT_CHANEL)

    # local methods

    def _get_current_time(self) -> int:
        """Get millisec time since starting handler."""
        return int(1000 * (time.time() - self._start_time))

    def _send_connection_packet(self, packet: ConnectionPacket, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: frame reliability
        """
        _logger.debug('< %s', LogString(packet))
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    def _send_game_packet_immediately(self, packet: GamePacket, addr: Address) -> None:
        self._queue.send_immediately(packet, addr)

    # packet handling methods

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
        self._accepted_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
            to_packet_format(addr),
            0,
            self._INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr])
        self._send_connection_packet(res_packet, addr, DEFAULT_CHANEL)

    def _process_new_incoming_connection(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning('The packet of new incoming connection has invalid time. (expected:%d, actual: %d)',
                            self._accepted_time[addr], packet.server_time_since_start)
            return

        self._ping_time[addr] = self._get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTED_PING,
            self._get_current_time())
        self._send_connection_packet(res_packet, addr, UNRELIABLE)

        self._session_manager.append(addr)

    def _process_disconnection_notification(self, packet: ConnectionPacket, addr: Address) -> None:
        player = self._session_manager[addr]
        del self._session_manager[addr]
        self._send_connection_packet(packet, addr, DEFAULT_CHANEL)
        text_packet = game_packet_factory.create(
            GamePacketType.TEXT,
            EXTRA_DATA,
            TextType.TRANSLATION,
            False,
            None,
            EscapeSequence.YELLOW.value + '%multiplayer.player.left',
            (player.name, ),
            ''
        )
        remove_entity_packet = game_packet_factory.create(
            GamePacketType.REMOVE_ENTITY,
            EXTRA_DATA,
            player.entity_unique_id
        )
        remove_player_packet = game_packet_factory.create(
            GamePacketType.PLAYER_LIST,
            EXTRA_DATA,
            PlayerListType.REMOVE,
            (PlayerListEntry(player.id, None, None, None, None), )
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet_immediately(text_packet, addr)
            self._send_game_packet_immediately(remove_entity_packet, addr)
            self._send_game_packet_immediately(remove_player_packet, addr)
        raise SessionNotFound(addr)

    def _process_batch(self, packet: ConnectionPacket, addr: Address) -> None:
        for data in packet.payloads:
            try:
                packet = game_packet_codec.decode(data)
                _logger.debug('> %s', LogString(packet))
                getattr(self, '_process_' + GamePacketType(packet.id).name.lower())(packet, addr)
            except KeyError as exc:
                _logger.warning('%s is not supported in batch processing.', exc)

    def _process_login(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        player_data = packet.connection_request.player_data
        client_data = packet.connection_request.client_data
        # TODO check the logged-in player and log out the same player
        player.login(
            packet.protocol, player_data, client_data,
            login_sequence(player, addr, self._session_manager, self._world, self._send_game_packet_immediately))
        self._session_manager.bind(player.id, addr)

        res_packet = game_packet_factory.create(GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self._send_game_packet_immediately(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self._send_game_packet_immediately(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: GamePacket, addr: Address) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:
            res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self._send_game_packet_immediately(res_packet, addr)
        elif packet.status == ResourcePackStatus.COMPLETED:
            player = self._session_manager[addr]
            self._world.perform(action_factory.create(ActionType.LOGIN_PLAYER, player.id))

    def _process_request_chunk_radius(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        player.update_required_chunk(packet.radius)
        self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, player.next_required_chunk()))
        res_packet = game_packet_factory.create(GamePacketType.CHUNK_RADIUS_UPDATED, EXTRA_DATA, packet.radius)
        self._send_game_packet_immediately(res_packet, addr)

    # noinspection PyUnusedLocal
    def _process_move_player(self, packet: GamePacket, addr: Address) -> None:
        assert packet.mode != MoveMode.TELEPORT
        self._world.perform(action_factory.create(
            ActionType.MOVE_PLAYER,
            packet.entity_runtime_id,
            packet.position,
            packet.pitch,
            packet.yaw,
            packet.head_yaw,
            packet.mode,
            packet.on_ground,
            packet.riding_eid
        ))

    def _process_sound_event(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        for addr, p in self._session_manager.excluding(player):
            self._send_game_packet_immediately(packet, addr)

    def _process_player_action(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        # noinspection PyProtectedMember
        res_packet = packet._replace(entity_runtime_id=player.entity_runtime_id)
        for addr, p in self._session_manager.excluding(player):
            self._send_game_packet_immediately(res_packet, addr)

    # event handling methods

    def _process_event_player_logged_in(self, event: Event) -> None:
        player = self._session_manager[event.player_id]
        player.next_login_sequence(event)

    def _process_event_inventory_loaded(self, event: Event) -> None:
        player = self._session_manager[event.player_id]
        player.next_login_sequence(event)

    def _process_event_slot_initialized(self, event: Event) -> None:
        player = self._session_manager[event.player_id]
        player.next_login_sequence(event)

    def _process_event_full_chunk_loaded(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.FULL_CHUNK_DATA, EXTRA_DATA, event.position, event.data)
        for addr, player in self._session_manager:
            if player.did_request_chunk(event.position):
                self._send_game_packet_immediately(res_packet, addr)
                player.discard_chunk_request(event.position)
                player.next_login_sequence(event)

    def _process_event_player_moved(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.MOVE_PLAYER,
            EXTRA_DATA,
            event.entity_runtime_id,
            event.position,
            event.pitch,
            event.yaw,
            event.head_yaw,
            event.mode,
            event.on_ground,
            event.riding_eid,
            None,
            None
        )
        for addr, player in self._session_manager:
            if player.entity_runtime_id != event.entity_runtime_id:
                self._send_game_packet_immediately(res_packet, addr)
            else:
                player.position = event.position
                self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, player.next_required_chunk()))
