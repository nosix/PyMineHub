from typing import NamedTuple as _NamedTuple, Dict, Tuple

from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.value import PlayerID, EntityUniqueID, EntityRuntimeID


class EntitySpec(_NamedTuple('EntitySpec', [
    ('eye_height', float)
])):
    pass


_PLAYER_ENTITY_SPEC = EntitySpec(1.625)


class Entity:

    def __init__(self, spec: EntitySpec, entity_unique_id: EntityUniqueID) -> None:
        self._spec = spec
        self._entity_unique_id = entity_unique_id
        self._spawn_position = Vector3(256, 56, 256)
        self._position = Vector3(0.0, 0.0, 0.0)
        self._pitch = 0.0
        self._yaw = 0.0

    def spawn(self, block_height: int) -> None:
        y = self._spawn_position.y if self._spawn_position.y > block_height else block_height
        self._position = self._spawn_position.copy(y=y + self._spec.eye_height)

    @property
    def entity_unique_id(self) -> EntityUniqueID:
        return self._entity_unique_id

    @property
    def sapwn_position(self) -> Vector3[int]:
        return self._spawn_position

    @sapwn_position.setter
    def spawn_position(self, value: Vector3[int]) -> None:
        self._spawn_position = value

    @property
    def position(self) -> Vector3[float]:
        return self._position

    @position.setter
    def position(self, value: Vector3[float]) -> None:
        self._position = value

    @property
    def pitch(self) -> float:
        return self._pitch

    @pitch.setter
    def pitch(self, value: float) -> None:
        self._pitch = value

    @property
    def yaw(self) -> float:
        return self._yaw

    @yaw.setter
    def yaw(self, value: float) -> None:
        self._yaw = value


class PlayerEntity(Entity):

    def __init__(self, player_id: PlayerID, entity_unique_id: EntityUniqueID) -> None:
        super().__init__(_PLAYER_ENTITY_SPEC, entity_unique_id)
        self._player_id = player_id
        self._health = 20.0
        self._hunger = 20.0

    @property
    def player_id(self) -> PlayerID:
        return self._player_id

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float) -> None:
        self._health = value

    @property
    def hunger(self) -> float:
        return self._hunger

    @hunger.setter
    def hunger(self, value: float) -> None:
        self._hunger = value


class EntityPool:

    def __init__(self) -> None:
        self._players = {}  # type: Dict[EntityRuntimeID, PlayerEntity]
        self._entities = {}  # type: Dict[EntityRuntimeID, Entity]
        self._last_entity_id = 1

    def _next_entity_id(self) -> Tuple[EntityUniqueID, EntityRuntimeID]:
        self._last_entity_id += 1
        return self._last_entity_id, self._last_entity_id

    def __getitem__(self, entity_runtime_id: EntityRuntimeID) -> Entity:
        return self._entities[entity_runtime_id]

    def load_player(self, player_id: PlayerID) -> EntityRuntimeID:
        for entity_runtime_id, entity in self._players.items():
            if entity.player_id == player_id:
                return entity_runtime_id
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = PlayerEntity(player_id, entity_unique_id)
        # TODO load from database
        self._entities[entity_runtime_id] = entity
        self._players[entity_runtime_id] = entity
        return entity_runtime_id

    def get_player(self, entity_runtime_id: EntityRuntimeID) -> PlayerEntity:
        return self._players[entity_runtime_id]
