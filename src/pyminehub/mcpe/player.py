import uuid
from typing import Set

from pyminehub.mcpe.value import *


class Player:

    def __init__(self) -> None:
        self._uuid = uuid.uuid4()
        self._protocol = None
        self._player_data = None
        self._client_data = None
        self._entity_unique_id = 0
        self._entity_runtime_id = 0
        self._metadata_flags = None
        self._position = Vector3(256.0, 57.625, 256.0)
        self._requested_chunk_position = set()  # type: Set[ChunkPosition]
        self._near_chunk_position = set()  # type: Set[ChunkPosition]
        self._is_living = False

    def login(self, protocol: int, player_data: PlayerData, client_data: ClientData) -> None:
        self._protocol = protocol
        self._player_data = player_data
        self._client_data = client_data

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def id(self) -> PlayerID:
        return self._player_data.xuid

    @property
    def name(self) -> str:
        assert self._player_data
        return self._player_data.display_name

    @property
    def skin(self) -> Skin:
        assert self._client_data
        return self._client_data.skin

    @property
    def entity_unique_id(self) -> EntityUniqueID:
        assert self._entity_unique_id != 0
        return self._entity_unique_id

    @entity_unique_id.setter
    def entity_unique_id(self, value: EntityUniqueID) -> None:
        self._entity_unique_id = value

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        assert self._entity_runtime_id != 0
        return self._entity_runtime_id

    @entity_runtime_id.setter
    def entity_runtime_id(self, value: EntityRuntimeID) -> None:
        self._entity_runtime_id = value

    @property
    def position(self) -> Vector3[float]:
        return self._position

    @position.setter
    def position(self, value: Vector3[float]) -> None:
        self._position = value

    @property
    def metadata_flags(self) -> EntityMetaDataFlagValue:
        assert self._metadata_flags
        return self._metadata_flags

    @metadata_flags.setter
    def metadata_flags(self, value: EntityMetaDataFlagValue) -> None:
        self._metadata_flags = value

    def get_required_chunk(self, radius: int) -> Tuple[ChunkPositionWithDistance, ...]:
        request = tuple(to_chunk_area(self._position, radius))
        self._requested_chunk_position |= set(p.position for p in request)
        self._near_chunk_position = set(p.position for p in to_chunk_area(self._position, 2))
        return request

    def did_request_chunk(self, position: ChunkPosition) -> bool:
        return position in self._requested_chunk_position

    def discard_chunk_request(self, position: ChunkPosition) -> None:
        self._requested_chunk_position.discard(position)

    def is_living(self) -> bool:
        return self._is_living

    def is_ready(self) -> bool:
        return len(self._requested_chunk_position - self._near_chunk_position) == 0

    def sapwn(self) -> None:
        self._is_living = True
