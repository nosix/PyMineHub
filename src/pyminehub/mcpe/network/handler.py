import time
from logging import getLogger

from pyminehub.mcpe.action import ActionType, action_factory
from pyminehub.mcpe.command import CommandRegistry, CommandContextImpl
from pyminehub.mcpe.event import EventType, Event
from pyminehub.mcpe.metadata import create_entity_metadata
from pyminehub.mcpe.network.codec import connection_packet_codec, game_packet_codec
from pyminehub.mcpe.network.login import login_sequence
from pyminehub.mcpe.network.packet import *
from pyminehub.mcpe.network.queue import GamePacketQueue
from pyminehub.mcpe.network.reliability import UNRELIABLE, DEFAULT_CHANEL
from pyminehub.mcpe.network.session import SessionManager
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address, get_unspecified_address, to_packet_format
from pyminehub.raknet import Reliability, SessionNotFound, GameDataHandler
from pyminehub.value import LogString

_logger = getLogger(__name__)


_NONE_INVENTORY_SLOT = 255


class MCPEHandler(GameDataHandler):

    _INTERNAL_ADDRESSES = tuple(to_packet_format((get_unspecified_address(), 0)) for _ in range(20))

    def __init__(self, world: WorldProxy, command: CommandRegistry) -> None:
        self._world = world
        self._command = command
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
        getattr(self, '_process_' + packet.type.name.lower())(packet, addr)

    async def update(self) -> None:
        event = await self._world.next_event()
        getattr(self, '_process_event_' + event.type.name.lower())(event)

    def terminate(self) -> None:
        res_packet = connection_packet_factory.create(ConnectionPacketType.DISCONNECTION_NOTIFICATION)
        for addr in self._session_manager.addresses:
            self._send_connection_packet(res_packet, addr, DEFAULT_CHANEL)
        self._world.terminate()

    # local methods

    def _get_current_time(self) -> int:
        """Get millisecond time since starting handler."""
        return int(1000 * (time.time() - self._start_time))

    def _send_connection_packet(self, packet: ConnectionPacket, addr: Address, reliability: Reliability) -> None:
        """Send connection packet to specified address.

        :param packet: connection packet
        :param addr: destination
        :param reliability: frame reliability
        """
        _logger.debug('< %s', LogString(packet))
        self.sendto(connection_packet_codec.encode(packet), addr, reliability)

    def _send_game_packet(self, packet: GamePacket, addr: Address, immediately=True) -> None:
        if immediately:
            self._queue.send_immediately(packet, addr)
        else:
            self._queue.append(packet, addr)

    def _send_waiting_game_packet(self) -> None:
        self._queue.send()

    def _forward_packet_to_other_players(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        player = self._session_manager[addr]
        for addr, p in self._session_manager.excluding(player):
            self._send_game_packet(packet, addr, is_last)

    @staticmethod
    def _to_internal_format_hotbar(inventory_slot: int) -> Optional[int]:
        return inventory_slot - HOTBAR_SIZE if inventory_slot != -1 else None

    @staticmethod
    def _mob_spawned_event_to_metadata(event: Event) -> Tuple[EntityMetaData, ...]:
        if event.name is None:
            return tuple()
        else:
            return (
                create_entity_metadata(EntityMetaDataKey.FLAGS, EntityMetaDataFlagValue.create(
                    always_show_nametag=True
                ).flags),
                create_entity_metadata(EntityMetaDataKey.NAMETAG, event.name),
            )

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
        self._world.perform(action_factory.create(
            ActionType.LOGOUT_PLAYER,
            player.entity_runtime_id
        ))
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
            self._send_game_packet(text_packet, addr)
            self._send_game_packet(remove_entity_packet, addr)
            self._send_game_packet(remove_player_packet, addr)
        raise SessionNotFound(addr)

    def _process_batch(self, packet: ConnectionPacket, addr: Address) -> None:
        last_index = len(packet.payloads) - 1
        for i, data in enumerate(packet.payloads):
            try:
                packet = game_packet_codec.decode(data)
                _logger.debug('> %s', LogString(packet))
                getattr(self, '_process_' + packet.type.name.lower())(packet, addr, i == last_index)
            except AttributeError as exc:
                _logger.warning('%s', exc)
            except KeyError as exc:
                _logger.warning('%s is not supported in batch processing.', exc)

    def _process_login(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert is_last
        player = self._session_manager[addr]
        player_data = packet.connection_request.player_data
        client_data = packet.connection_request.client_data
        # TODO check the logged-in player and log out the same player
        player.login(
            packet.protocol, player_data, client_data,
            login_sequence(player, addr, self._session_manager, self._world, self._command, self._send_game_packet))
        self._session_manager.bind(player.id, addr)

        res_packet = game_packet_factory.create(GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self._send_game_packet(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self._send_game_packet(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert is_last
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:
            res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self._send_game_packet(res_packet, addr)
        elif packet.status == ResourcePackStatus.COMPLETED:
            player = self._session_manager[addr]
            self._world.perform(action_factory.create(ActionType.LOGIN_PLAYER, player.id))

    def _process_request_chunk_radius(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert is_last
        player = self._session_manager[addr]
        player.update_required_chunk(packet.radius)
        required_chunk = player.next_required_chunk()
        if len(required_chunk) > 0:
            self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, required_chunk))
        res_packet = game_packet_factory.create(GamePacketType.CHUNK_RADIUS_UPDATED, EXTRA_DATA, packet.radius)
        self._send_game_packet(res_packet, addr)

    def _process_move_player(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert packet.entity_runtime_id == self._session_manager[addr].entity_runtime_id
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
        if is_last:
            self._send_waiting_game_packet()

    def _process_player_action(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        self._forward_packet_to_other_players(packet, addr, is_last)

    def _process_sound_event(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        self._forward_packet_to_other_players(packet, addr, is_last)

    def _process_animate(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        self._forward_packet_to_other_players(packet, addr, is_last)

    def _process_space_event(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        self._forward_packet_to_other_players(packet, addr, is_last)

    def _process_interact(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        pass  # TODO implement

    def _process_inventory_transaction(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        player = self._session_manager[addr]
        if packet.transaction_type == InventoryTransactionType.USE_ITEM:
            if packet.data.action_type == UseItemActionType.BREAK_BLOCK:
                self._world.perform(action_factory.create(
                    ActionType.BREAK_BLOCK,
                    player.entity_runtime_id,
                    packet.data.position
                ))
            elif packet.data.action_type == UseItemActionType.CLICK_BLOCK:
                if packet.data.item_in_hand.type != ItemType.AIR:
                    self._world.perform(action_factory.create(
                        ActionType.PUT_ITEM,
                        player.entity_runtime_id,
                        packet.data.position,
                        packet.data.face,
                        packet.data.hotbar_slot,
                        packet.data.item_in_hand
                    ))
        if is_last:
            self._send_waiting_game_packet()

    def _process_mob_equipment(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert packet.entity_runtime_id == self._session_manager[addr].entity_runtime_id
        if packet.window_type == WindowType.INVENTORY:
            self._world.perform(action_factory.create(
                ActionType.EQUIP,
                packet.entity_runtime_id,
                packet.inventory_slot - HOTBAR_SIZE if packet.inventory_slot != _NONE_INVENTORY_SLOT else None,
                packet.hotbar_slot,
                packet.item
            ))
        if is_last:
            self._send_waiting_game_packet()

    def _process_player_hotbar(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        player = self._session_manager[addr]
        if packet.window_type == WindowType.INVENTORY:
            self._world.perform(action_factory.create(
                ActionType.SET_HOTBAR,
                player.entity_runtime_id,
                packet.selected_hotbar_slot,
                tuple(self._to_internal_format_hotbar(slot) for slot in packet.slots)
            ))
        else:
            raise NotImplementedError()
        if is_last:
            self._send_waiting_game_packet()

    def _process_command_request(self, packet: GamePacket, addr: Address, is_last: bool) -> None:
        assert packet.command[0] == '/'
        func = self._command.execute_command(packet.command[1:])  # TODO pass arguments

        if packet.origin_data.type == CommandOriginDataType.PLAYER:
            def send_text(text: str, broadcast: bool):
                nonlocal addr
                text_packet = game_packet_factory.create(
                    GamePacketType.TEXT,
                    EXTRA_DATA,
                    TextType.TRANSLATION,
                    False,
                    None,
                    text,
                    (),
                    ''
                )
                if broadcast:
                    for addr in self._session_manager.addresses:
                        self._send_game_packet(text_packet, addr)
                else:
                    self._send_game_packet(text_packet, addr)

            func(CommandContextImpl(send_text))  # TODO more complex feature
        if is_last:
            self._send_waiting_game_packet()

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
                self._send_game_packet(res_packet, addr)
                player.discard_chunk_request(event.position)
                if player.next_login_sequence(event):
                    self._world.perform(action_factory.create(
                        ActionType.REQUEST_ENTITY,
                        player.entity_runtime_id
                    ))

    def _process_event_entity_loaded(self, event: Event) -> None:
        addr = self._session_manager.get_address(event.player_id)
        for e in event.spawn_events:
            if e.type == EventType.ITEM_SPAWNED:
                res_packet = game_packet_factory.create(
                    GamePacketType.ADD_ITEM_ENTITY,
                    EXTRA_DATA,
                    e.entity_unique_id,
                    e.entity_runtime_id,
                    e.item,
                    e.position,
                    e.motion,
                    e.metadata
                )
                self._send_game_packet(res_packet, addr, immediately=False)
            if e.type == EventType.MOB_SPAWNED:
                print(e.entity_type)
                res_packet = game_packet_factory.create(
                    GamePacketType.ADD_ENTITY,
                    EXTRA_DATA,
                    e.entity_unique_id,
                    e.entity_runtime_id,
                    e.entity_type,
                    e.position,
                    Vector3(0.0, 0.0, 0.0),
                    e.pitch,
                    e.yaw,
                    tuple(),
                    self._mob_spawned_event_to_metadata(e),
                    tuple()
                )
                self._send_game_packet(res_packet, addr, immediately=False)
        self._send_waiting_game_packet()

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
                self._send_game_packet(res_packet, addr)
            else:
                player.position = event.position
                player.yaw = event.yaw
                required_chunk = player.next_required_chunk()
                if len(required_chunk) > 0:
                    self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, required_chunk))

    def _process_event_block_updated(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.UPDATE_BLOCK,
            EXTRA_DATA,
            event.position,
            event.block
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet(res_packet, addr)

    def _process_event_item_spawned(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.ADD_ITEM_ENTITY,
            EXTRA_DATA,
            event.entity_unique_id,
            event.entity_runtime_id,
            event.item,
            event.position,
            event.motion,
            event.metadata
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet(res_packet, addr)

    def _process_event_item_taken(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.TAKE_ITEM_ENTITY,
            EXTRA_DATA,
            event.item_runtime_id,
            event.player_runtime_id
        )
        for addr, player in self._session_manager:
            self._send_game_packet(res_packet, addr)

    def _process_event_inventory_updated(self, event: Event) -> None:
        addr = self._session_manager.get_address(event.player_id)
        res_packet = game_packet_factory.create(
            GamePacketType.INVENTORY_SLOT,
            EXTRA_DATA,
            WindowType.INVENTORY,
            event.inventory_slot,
            event.slot_item
        )
        self._send_game_packet(res_packet, addr)

    def _process_event_entity_removed(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.REMOVE_ENTITY,
            EXTRA_DATA,
            event.entity_runtime_id
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet(res_packet, addr)

    def _process_event_equipment_updated(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.MOB_EQUIPMENT,
            EXTRA_DATA,
            event.entity_runtime_id,
            event.equipped_item,
            event.inventory_slot + HOTBAR_SIZE if event.inventory_slot is not None else _NONE_INVENTORY_SLOT,
            event.hotbar_slot,
            WindowType.INVENTORY
        )
        for addr, player in self._session_manager:
            if player.entity_runtime_id == event.entity_runtime_id:
                player.equipped_item = event.equipped_item
            self._send_game_packet(res_packet, addr)

    def _process_event_mob_spawned(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.ADD_ENTITY,
            EXTRA_DATA,
            event.entity_unique_id,
            event.entity_runtime_id,
            event.entity_type,
            event.position,
            Vector3(0.0, 0.0, 0.0),
            event.pitch,
            event.yaw,
            tuple(),
            self._mob_spawned_event_to_metadata(event),
            tuple()
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet(res_packet, addr)

    def _process_event_mob_moved(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.MOVE_ENTITY,
            EXTRA_DATA,
            event.entity_runtime_id,
            event.position,
            event.pitch,
            0.0,
            event.yaw,
            event.on_ground,
            False
        )
        for addr in self._session_manager.addresses:
            self._send_game_packet(res_packet, addr)
