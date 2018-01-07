from pyminehub.mcpe.value import EntityRuntimeID, Item


class WorldEditor:

    def remove_entity(self, entity_runtime_id: EntityRuntimeID) -> None:
        raise NotImplementedError()

    def append_to_player_inventory(self, entity_runtime_id: EntityRuntimeID, item: Item) -> int:
        raise NotImplementedError()
