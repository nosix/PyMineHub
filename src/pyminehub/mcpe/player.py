from typing import Set, Tuple

from pyminehub.mcpe.geometry import Vector3, ChunkPositionWithDistance, to_chunk_area, ChunkPosition
from pyminehub.mcpe.value import PlayerData, ClientData, PlayerID, EntityRuntimeID


class Player:

    def __init__(self) -> None:
        self._protocol = None
        self._player_data = None
        self._client_data = None
        self._entity_runtime_id = 0
        self._position = Vector3(256.0, 57.625, 256.0)
        self._requested_chunk_position = set()  # type: Set[ChunkPosition]
        self._near_chunk_position = set()  # type: Set[ChunkPosition]
        self._is_living = False

    @property
    def id(self) -> PlayerID:
        return self._player_data.xuid

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        assert self._entity_runtime_id != 0
        return self._entity_runtime_id

    @entity_runtime_id.setter
    def entity_runtime_id(self, entity_runtime_id: EntityRuntimeID) -> None:
        self._entity_runtime_id = entity_runtime_id

    @property
    def position(self) -> Vector3[float]:
        return self._position

    @position.setter
    def position(self, position: Vector3[float]) -> None:
        self._position = position

    def login(self, protocol: int, player_data: PlayerData, client_data: ClientData) -> None:
        self._protocol = protocol
        self._player_data = player_data
        self._client_data = client_data

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
