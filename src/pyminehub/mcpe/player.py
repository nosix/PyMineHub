from pkgutil import get_data
from typing import Dict, List, Set, Tuple, Union

from pyminehub.mcpe.const import GameMode, PlayerPermission
from pyminehub.mcpe.geometry import Vector3, ChunkPositionWithDistance, to_chunk_area, ChunkPosition
from pyminehub.mcpe.value import PlayerData, ClientData, Slot, PlayerID, EntityUniqueID, EntityRuntimeID

_INVENTORY_CONTENT_ITEMS = get_data(__package__, 'inventory-content-items121.dat')


class Player:

    def __init__(self) -> None:
        self._protocol = None
        self._player_data = None
        self._client_data = None
        self._entity_unique_id = 1
        self._entity_runtime_id = 1
        self._game_mode = GameMode.SURVIVAL
        self._position = Vector3(256.0, 57.625, 256.0)
        self._pitch = 0.0
        self._yaw = 358.0
        self._spawn = Vector3(512, 56, 512)
        self._permission = PlayerPermission.MEMBER
        self._inventory_content = {}  # type: Dict[int, List[Slot]]
        self._requested_chunk_position = set()  # type: Set[ChunkPosition]

    def get_id(self) -> PlayerID:
        return self._player_data.xuid

    def login(self, protocol: int, player_data: PlayerData, client_data: ClientData) -> None:
        self._protocol = protocol
        self._player_data = player_data
        self._client_data = client_data

    def get_entity_unique_id(self) -> EntityUniqueID:
        return self._entity_unique_id

    def get_entity_runtime_id(self) -> EntityRuntimeID:
        return self._entity_runtime_id

    def get_game_mode(self) -> GameMode:
        return self._game_mode

    def get_position(self) -> Vector3[float]:
        return self._position

    def get_pitch(self) -> float:
        return self._pitch

    def get_yaw(self) -> float:
        return self._yaw

    def get_sapwn(self) -> Vector3[int]:
        return self._spawn

    def get_permission(self) -> PlayerPermission:
        return self._permission

    def get_inventory_content(self, window_id: int) -> Union[Tuple[Slot, ...], bytes]:
        return tuple(self._inventory_content[window_id]) if window_id != 121 else _INVENTORY_CONTENT_ITEMS

    def get_required_chunk(self, radius: int) -> Tuple[ChunkPositionWithDistance, ...]:
        request = tuple(to_chunk_area(self._position, radius))
        self._requested_chunk_position |= set(p.position for p in request)
        return request

    def did_request_chunk(self, position: ChunkPosition) -> bool:
        return position in self._requested_chunk_position

    def discard_chunk_request(self, position: ChunkPosition) -> None:
        self._requested_chunk_position.discard(position)
