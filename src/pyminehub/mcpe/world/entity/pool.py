from typing import Dict, List, Tuple

from pyminehub.mcpe.value import PlayerID, EntityUniqueID, EntityRuntimeID, Item
from pyminehub.mcpe.world.database import DataBase, Player
from pyminehub.mcpe.world.entity.collision import Collision, CollisionWithItem
from pyminehub.mcpe.world.entity.instance import PlayerEntity, ItemEntity


class EntityPool:

    def __init__(self, db: DataBase) -> None:
        self._db = db
        self._players = {}  # type: Dict[EntityRuntimeID, PlayerEntity]
        self._items = {}  # type: Dict[EntityRuntimeID, ItemEntity]
        self._last_entity_id = 0

    def _next_entity_id(self) -> Tuple[EntityUniqueID, EntityRuntimeID]:
        self._last_entity_id += 1
        return self._last_entity_id, self._last_entity_id

    def load_player(self, player_id: PlayerID) -> EntityRuntimeID:
        for entity_runtime_id, entity in self._players.items():
            if entity.player_id == player_id:
                return entity_runtime_id
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = PlayerEntity(player_id, entity_unique_id, entity_runtime_id)
        player = self._db.load_player(str(player_id))
        if player is not None:
            entity.spawn_position = player.spawn_position
            entity.position = player.position
            entity.yaw = player.yaw
            entity.health = player.health
            entity.hunger = player.hunger
            entity.air = player.air
        self._players[entity_runtime_id] = entity
        return entity_runtime_id

    def _save_player(self, entity_runtime_id: EntityRuntimeID) -> None:
        player = self._players[entity_runtime_id]
        self._db.save_player(Player(
            str(player.player_id),
            player.spawn_position,
            player.position,
            player.yaw,
            player.health,
            player.hunger,
            player.air
        ))

    def get_player(self, entity_runtime_id: EntityRuntimeID) -> PlayerEntity:
        return self._players[entity_runtime_id]

    def create_item(self, item: Item) -> EntityRuntimeID:
        entity_unique_id, entity_runtime_id = self._next_entity_id()
        entity = ItemEntity(item, entity_unique_id, entity_runtime_id)
        self._items[entity_runtime_id] = entity
        return entity_runtime_id

    def get_item(self, entity_runtime_id: EntityRuntimeID) -> ItemEntity:
        return self._items[entity_runtime_id]

    def remove(self, entity_runtime_id: EntityRuntimeID) -> None:
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
