import asyncio
import uuid
from enum import Enum
from logging import getLogger
from random import randrange
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

from pyminehub.mcpe.chunk import Chunk, decode_chunk
from pyminehub.mcpe.command.api import to_signature
from pyminehub.mcpe.command.const import CommandOriginDataType
from pyminehub.mcpe.command.value import CommandOriginData
from pyminehub.mcpe.const import EntityMetaDataKey
from pyminehub.mcpe.geometry import Vector3, ChunkPosition, to_local_position
from pyminehub.mcpe.network.const import PlayStatus, ResourcePackStatus
from pyminehub.mcpe.network.const import PlayerListType
from pyminehub.mcpe.network.handler import MCPEDataHandler
from pyminehub.mcpe.network.packet import *
from pyminehub.mcpe.network.reliability import RELIABLE, DEFAULT_CHANEL
from pyminehub.mcpe.network.skin import *
from pyminehub.mcpe.network.value import ConnectionRequest
from pyminehub.mcpe.value import EntityRuntimeID, EntityMetaData
from pyminehub.network.address import Address, to_packet_format
from pyminehub.raknet import AbstractClient

__all__ = [
    'MCPEClient',
    'ChunkInfo',
    'EntityInfo',
    'EntityEvent',
    'EntityEventListener'
]


_logger = getLogger(__name__)


class EntityEvent(Enum):
    ADDED = 1
    REMOVED = 2


EntityInfo = NamedTuple('EntityInfo', [
    ('entity_runtime_id', EntityRuntimeID),
    ('name', str),
    ('position', Vector3[float]),
    ('owner_runtime_id', Optional[EntityRuntimeID])
])

ChunkInfo = NamedTuple('ChunkInfo', [
    ('position', ChunkPosition),
    ('chunk', Chunk)
])


EntityEventListener = Callable[[EntityEvent, EntityInfo], None]


class _MutableEntityInfo:

    def __init__(self, entity_runtime_id: EntityRuntimeID, name: str) -> None:
        self._entity_runtime_id = entity_runtime_id
        self._name = name
        self._metadata = {}
        self._position = Vector3(0, 0, 0)

    @property
    def value(self) -> EntityInfo:
        return EntityInfo(
            self._entity_runtime_id, self.name, self._position, self.owner_runtime_id)

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        return self._entity_runtime_id

    @property
    def owner_runtime_id(self) -> Optional[EntityRuntimeID]:
        return self._metadata.get(EntityMetaDataKey.OWNER_EID, None)

    @property
    def name(self) -> str:
        return self._metadata.get(EntityMetaDataKey.NAMETAG, self._name)

    @property
    def position(self) -> Vector3[float]:
        return self._position

    @position.setter
    def position(self, value: Vector3[float]) -> None:
        self._position = value

    @property
    def metadata(self) -> Tuple[EntityMetaData, ...]:
        return tuple(self._metadata.values())

    @metadata.setter
    def metadata(self, value: Tuple[EntityMetaData, ...]) -> None:
        self._metadata = dict((m.key, m.value) for m in value)


class _MCPEClientHandler(MCPEDataHandler):

    def __init__(self) -> None:
        super().__init__()
        self._guid = randrange(1 << (8 * 8))  # long range
        self._uuid = uuid.uuid4()
        self._connecting = asyncio.Event()
        self._queue = asyncio.Queue()
        self._request_time = None
        self._is_active = asyncio.Event()
        self._entity_runtime_id = None  # type: EntityRuntimeID
        self._player_name = None  # type: str
        self._command_usage = []  # type: List[str]
        self._entities = {}  # type: Dict[EntityRuntimeID, _MutableEntityInfo]
        self._messages = []  # type: List[str]
        self._latest_chunk = None  # type: ChunkInfo
        self._processed = asyncio.Event()
        self._listener = None  # type: Optional[EntityEventListener]

    # GameDataHandler interface methods

    @property
    def guid(self) -> int:
        return self._guid

    def data_received(self, data: bytes, addr: Address) -> None:
        super().data_received(data, addr)
        self._processed.set()

    async def update(self) -> None:
        await asyncio.Event().wait()

    def terminate(self) -> None:
        pass

    # MCPEDataHandler method

    def update_status(self, addr: Address, is_connecting: bool) -> None:
        if is_connecting:
            self._connecting.set()

    # local methods

    @property
    def is_active(self) -> bool:
        return self._is_active.is_set()

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        assert self._entity_runtime_id is not None
        return self._entity_runtime_id

    @property
    def command_usage(self) -> str:
        return '\n'.join(self._command_usage)

    @property
    def latest_chunk(self) -> ChunkInfo:
        return self._latest_chunk

    @property
    def entities(self) -> Tuple[EntityInfo, ...]:
        return tuple(entity.value for entity in self._entities.values())

    def get_entity(self, entity_runtime_id: EntityRuntimeID) -> Optional[EntityInfo]:
        return self._entities[entity_runtime_id].value if entity_runtime_id in self._entities else None

    def next_message(self) -> Optional[str]:
        return self._messages.pop(0) if len(self._messages) > 0 else None

    def set_entity_event_listener(self, listener: Optional[EntityEventListener]) -> None:
        self._listener = listener

    async def start(self, server_addr: Address, player_name: str, locale: str) -> None:
        assert not self._is_active.is_set()
        self._request_time = self.get_current_time()
        self._player_name = player_name
        send_packet = connection_packet_factory.create(
            ConnectionPacketType.CONNECTION_REQUEST, self.guid, self._request_time, False)
        self.send_connection_packet(send_packet, server_addr, RELIABLE)
        await self._connecting.wait()

        send_packet = game_packet_factory.create(
            GamePacketType.LOGIN,
            EXTRA_DATA,
            160,  # TODO change
            ConnectionRequest(
                chain=(
                    {
                        'extraData': {
                            'XUID': '',
                            'identity': str(uuid.uuid4()),
                            'displayName': player_name,
                        },
                        'identityPublicKey': ''
                    },
                ),
                client={
                    'ClientRandomId': self.guid,
                    'LanguageCode': locale,
                    'CapeData': '',
                    'SkinId': DEFAULT_SKIN_ID,
                    'SkinGeometryName': DEFAULT_SKIN_GEOMETRY_NAME,
                    'SkinData': DEFAULT_SKIN_DATA,
                    'SkinGeometry': DEFAULT_SKIN_GEOMETRY,
                }
            )
        )
        self.send_game_packet(send_packet, server_addr)

        await self._is_active.wait()

    async def send_command_request(self, server_addr: Address, command: str) -> None:
        send_packet = game_packet_factory.create(
            GamePacketType.COMMAND_REQUEST,
            EXTRA_DATA,
            command,
            CommandOriginData(CommandOriginDataType.DEV_CONSOLE, self._uuid, '', 0),
            True
        )
        self.send_game_packet(send_packet, server_addr, DEFAULT_CHANEL)
        await asyncio.sleep(0.1)  # execute the send task

    async def wait_response(self) -> None:
        await self._processed.wait()
        self._processed.clear()

    def _process_connection_request_accepted(self, packet: ConnectionPacket, addr: Address) -> None:
        if packet.client_time_since_start != self._request_time:
            _logger.warning('The packet of connection request accepted has invalid time. (expected:%d, actual: %d)',
                            self._request_time, packet.client_time_since_start)
            return

        send_packet = connection_packet_factory.create(
            ConnectionPacketType.NEW_INCOMING_CONNECTION,
            to_packet_format(addr),
            self.INTERNAL_ADDRESSES,
            packet.server_time_since_start,
            self.get_current_time()
        )
        self.send_connection_packet(send_packet, addr, RELIABLE)

        self.send_ping(addr)

    # noinspection PyUnusedLocal
    def _process_disconnection_notification(self, packet: ConnectionPacket, addr: Address) -> None:
        self._is_active.clear()

    # noinspection PyUnusedLocal
    def _process_resource_packs_info(self, packet: GamePacket, addr: Address) -> None:
        send_packet = game_packet_factory.create(
            GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE,
            EXTRA_DATA,
            ResourcePackStatus.COMPLETED,
            ()
        )
        self.send_game_packet(send_packet, addr)

    # noinspection PyUnusedLocal
    def _process_play_status(self, packet: GamePacket, addr: Address) -> None:
        if packet.status == PlayStatus.LOGIN_SUCCESS:
            return
        if packet.status == PlayStatus.PLAYER_SPAWN:
            self._is_active.set()

    # noinspection PyUnusedLocal
    def _process_start_game(self, packet: GamePacket, addr: Address) -> None:
        self._entity_runtime_id = packet.entity_runtime_id
        entity = _MutableEntityInfo(packet.entity_runtime_id, self._player_name)
        entity.position = packet.player_position
        self._entities[entity.entity_runtime_id] = entity

    def _process_set_time(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_update_attributes(self, packet: GamePacket, addr: Address) -> None:
        pass

    # noinspection PyUnusedLocal
    def _process_set_entity_data(self, packet: GamePacket, addr: Address) -> None:
        entity = self._entities[packet.entity_runtime_id]
        entity.metadata = packet.metadata

    # noinspection PyUnusedLocal
    def _process_available_commands(self, packet: GamePacket, addr: Address) -> None:
        indent = '  '
        for command_data in packet.command_data:
            self._command_usage.append(command_data.description)
            for signature in to_signature(command_data, packet.enums):
                self._command_usage.append(indent + signature)

    def _process_adventure_settings(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_inventory_content(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_mob_equipment(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_inventory_slot(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_crafting_data(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_player_list(self, packet: GamePacket, addr: Address) -> None:
        _logger.info('%s %s: %d player', packet.type.name, packet.list_type.name, len(packet.entries))
        if packet.list_type is PlayerListType.ADD:
            for player in packet.entries:
                _logger.info('[%d] %s', player.entity_unique_id, player.user_name)
            if not self._is_active.is_set():
                send_packet = game_packet_factory.create(
                    GamePacketType.REQUEST_CHUNK_RADIUS,
                    EXTRA_DATA,
                    8
                )
                self.send_game_packet(send_packet, addr)

    def _process_chunk_radius_updated(self, packet: GamePacket, addr: Address) -> None:
        pass

    # noinspection PyUnusedLocal
    def _process_full_chunk_data(self, packet: GamePacket, addr: Address) -> None:
        self._latest_chunk = ChunkInfo(packet.position, decode_chunk(packet.data))

    # noinspection PyUnusedLocal
    def _process_add_player(self, packet: GamePacket, addr: Address) -> None:
        assert packet.entity_runtime_id == packet.entity_unique_id
        entity = _MutableEntityInfo(packet.entity_runtime_id, packet.user_name)
        entity.position = packet.position
        entity.metadata = packet.metadata
        self._entities[entity.entity_runtime_id] = entity
        if self._listener is not None:
            self._listener(EntityEvent.ADDED, entity.value)

    # noinspection PyUnusedLocal
    def _process_move_player(self, packet: GamePacket, addr: Address) -> None:
        entity = self._entities[packet.entity_runtime_id]
        entity.position = packet.position

    # noinspection PyUnusedLocal
    def _process_text(self, packet: GamePacket, addr: Address) -> None:
        # TODO check text_type and needs_translation
        parameters = tuple(str(p) for p in packet.parameters)
        message = '{} ({})'.format(packet.message, ', '.join(parameters)) if len(parameters) > 0 else packet.message
        _logger.info('%s: %s', packet.type.name, message)
        self._messages.append(message)

    # noinspection PyUnusedLocal
    def _process_add_entity(self, packet: GamePacket, addr: Address) -> None:
        name = 'anonymous:{}'.format(packet.entity_type.name)
        entity = _MutableEntityInfo(packet.entity_runtime_id, name)
        entity.position = packet.position
        entity.metadata = packet.metadata
        self._entities[entity.entity_runtime_id] = entity
        if self._listener is not None:
            self._listener(EntityEvent.ADDED, entity.value)

    # noinspection PyUnusedLocal
    def _process_remove_entity(self, packet: GamePacket, addr: Address) -> None:
        entity = self._entities[packet.entity_unique_id]
        del self._entities[packet.entity_unique_id]  # TODO map unique_id to runtime_id
        if self._listener is not None:
            self._listener(EntityEvent.REMOVED, entity.value)

    # noinspection PyUnusedLocal
    def _process_move_entity(self, packet: GamePacket, addr: Address) -> None:
        entity = self._entities[packet.entity_runtime_id]
        entity.position = packet.position

    # noinspection PyUnusedLocal
    def _process_update_block(self, packet: GamePacket, addr: Address) -> None:
        if self._latest_chunk is None:
            return
        if self._latest_chunk.position == ChunkPosition.at(packet.position):
            position_in_chunk = to_local_position(packet.position)
            self._latest_chunk.chunk.set_block(position_in_chunk, packet.block)

    def _process_sound_event(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_space_event(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_entity_event(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_player_action(self, packet: GamePacket, addr: Address) -> None:
        pass

    def _process_animate(self, packet: GamePacket, addr: Address) -> None:
        pass

    async def stop(self, server_addr: Address) -> None:
        send_packet = connection_packet_factory.create(
            ConnectionPacketType.DISCONNECTION_NOTIFICATION)
        self.send_connection_packet(send_packet, server_addr, RELIABLE)


class MCPEClient(AbstractClient):

    def __init__(self, player_name: str, locale: str) -> None:
        self._handler = _MCPEClientHandler()
        self._player_name = player_name
        self._locale = locale
        self._server_addr = None

    # AbstractClient methods

    @property
    def handler(self) -> _MCPEClientHandler:
        return self._handler

    async def start(self, server_addr: Address) -> None:
        self._server_addr = server_addr
        await self._handler.start(self._server_addr, self._player_name, self._locale)

    async def finished(self) -> None:
        await self._handler.stop(self._server_addr)

    # local methods

    @staticmethod
    async def _timeout(future: asyncio.Future, time: float) -> None:
        await asyncio.sleep(time)
        future.cancel()

    def wait_response(self, timeout: float=0) -> bool:
        """Wait until it receives a packet
        :param timeout: seconds. If it is 0 then timeout does not occur.
        :return: False if timeout occurred.
        """
        wait_future = asyncio.ensure_future(self._handler.wait_response())
        if timeout > 0:
            asyncio.ensure_future(self._timeout(wait_future, timeout))
        try:
            asyncio.get_event_loop().run_until_complete(wait_future)
            return True
        except asyncio.CancelledError:
            return False

    @property
    def is_active(self) -> bool:
        return self._handler.is_active

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        return self._handler.entity_runtime_id

    @property
    def command_usage(self) -> str:
        return self._handler.command_usage

    @property
    def latest_chunk(self) -> ChunkInfo:
        return self._handler.latest_chunk

    @property
    def entities(self) -> Tuple[EntityInfo, ...]:
        return self._handler.entities

    def get_entity(self, entity_runtime_id: EntityRuntimeID=None) -> Optional[EntityInfo]:
        return self._handler.get_entity(self.entity_runtime_id if entity_runtime_id is None else entity_runtime_id)

    def next_message(self) -> Optional[str]:
        return self._handler.next_message()

    def set_entity_event_listener(self, listener: Optional[EntityEventListener]) -> None:
        self._handler.set_entity_event_listener(listener)

    def execute_command(self, command: str) -> None:
        asyncio.get_event_loop().run_until_complete(self._handler.send_command_request(self._server_addr, command))
