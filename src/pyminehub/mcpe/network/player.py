from typing import Generator, Optional, Set, Tuple

from pyminehub.mcpe.const import PLAYER_EYE_HEIGHT, ItemType
from pyminehub.mcpe.event import Event
from pyminehub.mcpe.geometry import Vector3, ChunkPosition, ChunkPositionWithDistance, to_chunk_area
from pyminehub.mcpe.network.value import Skin, PlayerData, ClientData
from pyminehub.mcpe.value import *

__all__ = [
    'Player'
]


_NEAR_CHUNK_RADIUS = 2


class Player:

    def __init__(self, protocol: int, player_data: PlayerData, client_data: ClientData) -> None:
        self._protocol = protocol
        self._player_data = player_data
        self._client_data = client_data
        self._entity_unique_id = 0
        self._entity_runtime_id = 0
        self._position = Vector3(0.0, 0.0, 0.0)
        self._yaw = 0.0
        self._equipped_item = Item(ItemType.AIR, None, None, None, None)
        self._metadata = None
        self._chunk_radius = 0
        self._near_chunk_radius = _NEAR_CHUNK_RADIUS
        self._requested_chunk_position = set()  # type: Set[ChunkPosition]
        self._near_chunk_position = set()  # type: Set[ChunkPosition]
        self._is_living = False
        self._login_sequence = None
        self._monitored_entities = set()  # type: Set[EntityRuntimeID]

    def __eq__(self, other: 'Player') -> bool:
        assert isinstance(other, Player), type(other)
        return self.id == other.id

    def login(self, login_sequence: Generator[None, Event, None]) -> None:
        self._login_sequence = login_sequence
        login_sequence.send(None)

    def set_identity(self, entity_unique_id: EntityUniqueID, entity_runtime_id: EntityRuntimeID):
        self._entity_unique_id = entity_unique_id
        self._entity_runtime_id = entity_runtime_id

    @property
    def id(self) -> PlayerID:
        return self._player_data.identity

    @property
    def xuid(self) -> str:
        return self._player_data.xuid

    @property
    def name(self) -> str:
        return self._player_data.display_name

    @property
    def skin(self) -> Skin:
        return self._client_data.skin

    @property
    def entity_unique_id(self) -> EntityUniqueID:
        assert self._entity_unique_id != 0
        return self._entity_unique_id

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        assert self._entity_runtime_id != 0
        return self._entity_runtime_id

    @property
    def invisible(self) -> bool:
        return self.name == ''

    @property
    def bottom_position(self) -> Vector3[float]:
        return self._position - Vector3(0.0, PLAYER_EYE_HEIGHT, 0.0)

    @property
    def position(self) -> Vector3[float]:
        return self._position

    @position.setter
    def position(self, value: Vector3[float]) -> None:
        self._position = value

    @property
    def yaw(self) -> float:
        return self._yaw

    @yaw.setter
    def yaw(self, value: float) -> None:
        self._yaw = value

    @property
    def equipped_item(self) -> Item:
        return self._equipped_item

    @equipped_item.setter
    def equipped_item(self, value: Item) -> None:
        self._equipped_item = value

    @property
    def metadata(self) -> Tuple[EntityMetaData, ...]:
        return self._metadata

    @metadata.setter
    def metadata(self, value: Tuple[EntityMetaData, ...]) -> None:
        self._metadata = value

    @property
    def has_identity(self) -> bool:
        """True if login sequence is started"""
        return self._entity_runtime_id != 0 and self._entity_runtime_id != 0

    @property
    def is_ready(self) -> bool:
        """True if the surrounding chunks are complete"""
        return len(self._near_chunk_position) > 0 and \
            len(self._requested_chunk_position & self._near_chunk_position) == 0

    @property
    def is_living(self) -> bool:
        """True if login sequence is finished"""
        return self._is_living

    def next_required_chunk(self) -> Tuple[ChunkPositionWithDistance, ...]:
        if ChunkPosition.at(self._position) not in self._near_chunk_position:
            request = tuple(to_chunk_area(self._position, self._chunk_radius))
            request_chunk_position = set(p.position for p in request) - self._requested_chunk_position
            self._requested_chunk_position |= request_chunk_position
            self._near_chunk_position = set(p.position for p in request if p.distance <= self._near_chunk_radius)
            return tuple(p for p in request if p.position in request_chunk_position)
        else:
            return tuple()

    def update_required_chunk(self, radius: int) -> None:
        self._chunk_radius = radius
        self._near_chunk_radius = min(radius, _NEAR_CHUNK_RADIUS)
        self._near_chunk_position = set()

    def did_request_chunk(self, position: ChunkPosition) -> bool:
        return position in self._requested_chunk_position

    def discard_chunk_request(self, position: ChunkPosition) -> None:
        self._requested_chunk_position.discard(position)

    def next_login_sequence(self, event: Event) -> bool:
        """
        :param event: event passed to login sequence
        :return: True when login sequence is finished
        """
        if self._login_sequence is None:
            return False
        try:
            self._login_sequence.send(event)
            return False
        except StopIteration:
            self._is_living = True
            self._login_sequence = None
            return True

    def monitor_entity(self, entity_runtime_id: EntityRuntimeID) -> None:
        self._monitored_entities.add(entity_runtime_id)

    def does_monitor(self, entity_runtime_id: EntityRuntimeID, position: Optional[Vector3[float]]=None) -> bool:
        if entity_runtime_id in self._monitored_entities:
            return True if position is None else (ChunkPosition.at(position) in self._near_chunk_position)
        else:
            return False

    def removed_monitored(self, entity_runtime_id: EntityRuntimeID) -> None:
        self._monitored_entities.discard(entity_runtime_id)
