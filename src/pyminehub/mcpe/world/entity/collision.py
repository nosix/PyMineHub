from pyminehub.mcpe.event import Event, EventType, event_factory
from pyminehub.mcpe.world.entity.instance import PlayerEntity, ItemEntity
from pyminehub.mcpe.world.interface import WorldEditor


class Collision:

    def update(self, editor: WorldEditor) -> None:
        raise NotImplementedError()

    @property
    def event(self) -> Event:
        raise NotImplementedError()


class CollisionWithItem(Collision):

    def __init__(self, player_entity: PlayerEntity, item_entity: ItemEntity) -> None:
        self._player_entity = player_entity
        self._item_entity = item_entity

    def update(self, editor: WorldEditor) -> None:
        editor.append_to_player_inventory(self._player_entity.entity_runtime_id, self._item_entity.item)
        editor.remove_entity(self._item_entity.entity_runtime_id)

    @property
    def event(self) -> Event:
        return event_factory.create(
            EventType.ITEM_TAKEN,
            self._item_entity.entity_runtime_id,
            self._player_entity.entity_runtime_id
        )
