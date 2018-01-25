from logging import getLogger
from typing import Dict, Optional, Tuple

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.action import ActionType, action_factory
from pyminehub.mcpe.command.api import CommandRegistry
from pyminehub.mcpe.command.impl import CommandContextImpl
from pyminehub.mcpe.const import *
from pyminehub.mcpe.event import EventType, Event
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.metadata import create_entity_metadata
from pyminehub.mcpe.network.const import *
from pyminehub.mcpe.network.handler import MCPEDataHandler
from pyminehub.mcpe.network.login import login_sequence
from pyminehub.mcpe.network.packet import *
from pyminehub.mcpe.network.reliability import DEFAULT_CHANEL
from pyminehub.mcpe.network.session import SessionManager
from pyminehub.mcpe.network.value import PlayerListEntry
from pyminehub.mcpe.value import EntityMetaData, EntityMetaDataFlagValue
from pyminehub.mcpe.world import WorldProxy
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import SessionNotFound

__all__ = [
    'MCPEServerHandler'
]


_logger = getLogger(__name__)


_NONE_INVENTORY_SLOT = 255


class MCPEServerHandler(MCPEDataHandler):

    def __init__(self, world: WorldProxy, command: CommandRegistry) -> None:
        super().__init__()
        self._world = world
        self._command = command
        self._accepted_time = {}  # type: Dict[Address, int]
        self._session_manager = SessionManager()

    # GameDataHandler interface methods

    @property
    def guid(self) -> int:
        return get_value(ConfigKey.SERVER_GUID)

    async def update(self) -> None:
        event = await self._world.next_event()
        getattr(self, '_process_event_' + event.type.name.lower())(event)

    def terminate(self) -> None:
        res_packet = connection_packet_factory.create(ConnectionPacketType.DISCONNECTION_NOTIFICATION)
        for addr in self._session_manager.addresses:
            self.send_connection_packet(res_packet, addr, DEFAULT_CHANEL)
        self._world.terminate()

    # local methods

    def update_status(self, addr: Address, is_connecting: bool) -> None:
        pass  # TODO implement

    def _forward_packet_to_other_players(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        for addr, p in self._session_manager.excluding(player):
            self.send_game_packet(packet, addr, immediately=False)

    def _broadcast(self, packet: GamePacket) -> None:
        for addr in self._session_manager.addresses:
            self.send_game_packet(packet, addr)

    @staticmethod
    def _to_internal_format_hotbar(inventory_slot: int) -> Optional[int]:
        return inventory_slot - HOTBAR_SIZE if inventory_slot != -1 else None

    @staticmethod
    def _mob_spawned_event_to_metadata(event: Event) -> Tuple[EntityMetaData, ...]:
        metadata = []
        if event.name is not None:
            metadata.append(create_entity_metadata(EntityMetaDataKey.FLAGS, EntityMetaDataFlagValue.create(
                always_show_nametag=True
            ).flags))
            metadata.append(create_entity_metadata(EntityMetaDataKey.NAMETAG, event.name))
        if event.owner_runtime_id is not None:
            metadata.append(create_entity_metadata(EntityMetaDataKey.OWNER_EID, event.owner_runtime_id))
        return tuple(metadata)

    # packet handling methods

    def _process_connection_request(self, packet: ConnectionPacket, addr: Address) -> None:
        self._accepted_time[addr] = self.get_current_time()
        res_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
            to_packet_format(addr),
            0,
            self.INTERNAL_ADDRESSES,
            packet.client_time_since_start,
            self._accepted_time[addr])
        self.send_connection_packet(res_packet, addr, DEFAULT_CHANEL)

    def _process_new_incoming_connection(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.server_time_since_start != self._accepted_time[addr]:
            _logger.warning(
                'The packet of new incoming connection has invalid time. (expected: %d, actual: %d)',
                self._accepted_time[addr], packet.server_time_since_start)
            return

        self.send_ping(addr)
        self._session_manager.append(addr)

    def _process_disconnection_notification(self, packet: ConnectionPacket, addr: Address) -> None:
        player = self._session_manager[addr]
        self._world.perform(action_factory.create(
            ActionType.LOGOUT_PLAYER,
            player.entity_runtime_id
        ))
        del self._session_manager[addr]
        self.send_connection_packet(packet, addr, DEFAULT_CHANEL)
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
            self.send_game_packet(text_packet, addr)
            self.send_game_packet(remove_entity_packet, addr)
            self.send_game_packet(remove_player_packet, addr)
        raise SessionNotFound(addr)

    def _process_login(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        player_data = packet.connection_request.player_data
        client_data = packet.connection_request.client_data
        # TODO check the logged-in player and log out the same player
        player.login(
            packet.protocol, player_data, client_data,
            login_sequence(player, addr, self._session_manager, self._world, self._command, self.send_game_packet))
        self._session_manager.bind(player.id, addr)

        res_packet = game_packet_factory.create(GamePacketType.PLAY_STATUS, EXTRA_DATA, PlayStatus.LOGIN_SUCCESS)
        self.send_game_packet(res_packet, addr)
        res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACKS_INFO, EXTRA_DATA, False, (), ())
        self.send_game_packet(res_packet, addr)

    def _process_resource_pack_client_response(self, packet: GamePacket, addr: Address) -> None:
        if packet.status == ResourcePackStatus.SEND_PACKS:
            pass  # TODO do something?
        elif packet.status == ResourcePackStatus.HAVE_ALL_PACKS:
            res_packet = game_packet_factory.create(GamePacketType.RESOURCE_PACK_STACK, EXTRA_DATA, False, (), ())
            self.send_game_packet(res_packet, addr)
        elif packet.status == ResourcePackStatus.COMPLETED:
            player = self._session_manager[addr]
            self._world.perform(action_factory.create(ActionType.LOGIN_PLAYER, player.id))

    def _process_request_chunk_radius(self, packet: GamePacket, addr: Address) -> None:
        player = self._session_manager[addr]
        player.update_required_chunk(packet.radius)
        required_chunk = player.next_required_chunk()
        if len(required_chunk) > 0:
            self._world.perform(action_factory.create(ActionType.REQUEST_CHUNK, required_chunk))
        res_packet = game_packet_factory.create(GamePacketType.CHUNK_RADIUS_UPDATED, EXTRA_DATA, packet.radius)
        self.send_game_packet(res_packet, addr)

    def _process_move_player(self, packet: GamePacket, addr: Address) -> None:
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

    def _process_player_action(self, packet: GamePacket, addr: Address) -> None:
        self._forward_packet_to_other_players(packet, addr)

    def _process_sound_event(self, packet: GamePacket, addr: Address) -> None:
        self._forward_packet_to_other_players(packet, addr)

    def _process_animate(self, packet: GamePacket, addr: Address) -> None:
        self._forward_packet_to_other_players(packet, addr)

    def _process_space_event(self, packet: GamePacket, addr: Address) -> None:
        self._forward_packet_to_other_players(packet, addr)

    def _process_interact(self, packet: GamePacket, addr: Address) -> None:
        pass  # TODO implement

    def _process_inventory_transaction(self, packet: GamePacket, addr: Address) -> None:
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
                        packet.data.click_position,
                        packet.data.face,
                        packet.data.hotbar_slot,
                        packet.data.item_in_hand
                    ))
        if packet.transaction_type == InventoryTransactionType.NORMAL:
            is_creative = False
            for action in packet.actions:
                if action.source_type == SourceType.CREATIVE:
                    is_creative = True
                    continue
                if action.source_type == SourceType.CONTAINER:
                    assert is_creative, packet
                    assert action.window_type == WindowType.INVENTORY, action.window_type
                    self._world.perform(action_factory.create(
                        ActionType.SET_INVENTORY,
                        player.entity_runtime_id,
                        action.inventory_slot,
                        action.new_item
                    ))

    def _process_mob_equipment(self, packet: GamePacket, addr: Address) -> None:
        assert packet.entity_runtime_id == self._session_manager[addr].entity_runtime_id
        if packet.window_type == WindowType.INVENTORY:
            self._world.perform(action_factory.create(
                ActionType.EQUIP,
                packet.entity_runtime_id,
                packet.inventory_slot - HOTBAR_SIZE if packet.inventory_slot != _NONE_INVENTORY_SLOT else None,
                packet.hotbar_slot,
                packet.item
            ))

    def _process_player_hotbar(self, packet: GamePacket, addr: Address) -> None:
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

    def _process_command_request(self, packet: GamePacket, addr: Address) -> None:
        assert packet.command[0] == '/'

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
                    self.send_game_packet(text_packet, addr, immediately=False)
            else:
                self.send_game_packet(text_packet, addr, immediately=False)

        command_name, args = packet.command[1:].partition(' ')[0:3:2]
        context = CommandContextImpl(self._command, send_text, self._world.perform)
        self._command.execute_command(context, command_name, args)

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
                self.send_game_packet(res_packet, addr)
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
                self.send_game_packet(res_packet, addr, immediately=False)
            if e.type == EventType.MOB_SPAWNED:
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
                self.send_game_packet(res_packet, addr, immediately=False)
        self.send_waiting_game_packet()

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
                self.send_game_packet(res_packet, addr)
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
        self._broadcast(res_packet)

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
        self._broadcast(res_packet)

    def _process_event_item_taken(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.TAKE_ITEM_ENTITY,
            EXTRA_DATA,
            event.item_runtime_id,
            event.player_runtime_id
        )
        for addr, player in self._session_manager:
            self.send_game_packet(res_packet, addr)

    def _process_event_inventory_updated(self, event: Event) -> None:
        addr = self._session_manager.get_address(event.player_id)
        res_packet = game_packet_factory.create(
            GamePacketType.INVENTORY_SLOT,
            EXTRA_DATA,
            WindowType.INVENTORY,
            event.inventory_slot,
            event.slot_item
        )
        self.send_game_packet(res_packet, addr)

    def _process_event_entity_removed(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.REMOVE_ENTITY,
            EXTRA_DATA,
            event.entity_runtime_id
        )
        self._broadcast(res_packet)

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
            self.send_game_packet(res_packet, addr)

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
        self._broadcast(res_packet)

    def _process_event_mob_moved(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.MOVE_ENTITY,
            EXTRA_DATA,
            event.entity_runtime_id,
            event.position,
            event.pitch,
            event.yaw,
            0.0,
            event.on_ground,
            False
        )
        self._broadcast(res_packet)

    def _process_event_time_updated(self, event: Event) -> None:
        res_packet = game_packet_factory.create(
            GamePacketType.SET_TIME,
            EXTRA_DATA,
            event.time
        )
        self._broadcast(res_packet)
