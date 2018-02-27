from typing import Dict, Iterable, List, Optional, Tuple

from pyminehub.mcpe.const import WindowType, EntityType
from pyminehub.mcpe.datastore import DataStore
from pyminehub.mcpe.value import PlayerID, EntityUniqueID, EntityRuntimeID, Item, PlayerState
from pyminehub.mcpe.world.entity.collision import Collision, CollisionWithItem
from pyminehub.mcpe.world.entity.instance import PlayerEntity, ItemEntity, MobEntity

__all__ = [
    'EntityPool'
]


class EntityPool:

    def __init__(self, store: DataStore) -> None:
        self._store = store
        self._players = {}  # type: Dict[EntityRuntimeID, PlayerEntity]
        self._items = {}  # type: Dict[EntityRuntimeID, ItemEntity]
        self._mobs = {}  # type: Dict[EntityRuntimeID, MobEntity]
        self._last_entity_id = 0

    @property
    def players(self) -> Iterable[PlayerEntity]:
        return self._players.values()

    @property
    def items(self) -> Iterable[ItemEntity]:
        return self._items.values()

    @property
    def mobs(self) -> Iterable[MobEntity]:
        return self._mobs.values()

    def _next_entity_id(self) -> Tuple[EntityUniqueID, EntityRuntimeID]:
        self._last_entity_id += 1
        return self._last_entity_id, self._last_entity_id

    def load_player(self, player_id: PlayerID, is_guest: bool) -> EntityRuntimeID:
        for entity_runtime_id, entity in self._players.items():
            if entity.player_id == player_id:
                return entity_runtime_id
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = PlayerEntity(player_id, entity_unique_id, entity_runtime_id, is_guest)
        player = self._store.load_player(str(player_id)) if not is_guest else None
        if player is not None:
            entity.spawn_position = player.spawn_position
            entity.position = player.position
            entity.yaw = player.yaw
            entity.health = player.health
            entity.hunger = player.hunger
            entity.air = player.air
            entity.set_inventory(WindowType.INVENTORY, player.inventory)
            entity.set_inventory(WindowType.ARMOR, player.armor)
            entity.hotbar = player.hotbar
        self._players[entity_runtime_id] = entity
        return entity_runtime_id

    def _save_player(self, entity_runtime_id: EntityRuntimeID) -> None:
        player = self._players[entity_runtime_id]
        if player.is_guest:
            return
        self._store.save_player(
            str(player.player_id),
            PlayerState(
                player.spawn_position,
                player.position,
                player.yaw,
                player.health,
                player.hunger,
                player.air,
                player.get_inventory(WindowType.INVENTORY),
                player.get_inventory(WindowType.ARMOR),
                player.hotbar
            )
        )

    def get_player(self, entity_runtime_id: EntityRuntimeID) -> Optional[PlayerEntity]:
        return self._players.get(entity_runtime_id, None)

    def create_item(self, item: Item) -> EntityRuntimeID:
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = ItemEntity(item, entity_unique_id, entity_runtime_id)
        self._items[entity_runtime_id] = entity
        return entity_runtime_id

    def get_item(self, entity_runtime_id: EntityRuntimeID) -> Optional[ItemEntity]:
        return self._items.get(entity_runtime_id, None)

    def create_mob(self, entity_type: EntityType) -> EntityRuntimeID:
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = MobEntity(entity_type, entity_unique_id, entity_runtime_id)
        self._mobs[entity_runtime_id] = entity
        return entity_runtime_id

    def get_mob(self, entity_runtime_id: EntityRuntimeID) -> Optional[MobEntity]:
        return self._mobs.get(entity_runtime_id, None)

    def remove(self, entity_runtime_id: EntityRuntimeID) -> None:
        if entity_runtime_id in self._mobs:
            del self._mobs[entity_runtime_id]
        if entity_runtime_id in self._items:
            del self._items[entity_runtime_id]
        if entity_runtime_id in self._players:
            self._save_player(entity_runtime_id)
            del self._players[entity_runtime_id]

    def detect_collision(self, player_runtime_id: EntityRuntimeID) -> List[Collision]:
        player = self._players[player_runtime_id]
        collisions = []
        # TODO check only nearby chunks
        for item in self._items.values():
            if item.is_hit_by(player):
                collisions.append(CollisionWithItem(player, item))
        return collisions
