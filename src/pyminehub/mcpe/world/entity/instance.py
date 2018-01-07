from pyminehub.mcpe.const import WindowType
from pyminehub.mcpe.geometry import Vector3, OrientedBoundingBox
from pyminehub.mcpe.inventory import MutableInventory
from pyminehub.mcpe.resource import INVENTORY_CONTENT_ITEMS121
from pyminehub.mcpe.value import EntityUniqueID, EntityRuntimeID, PlayerID, Inventory, Slot
from pyminehub.mcpe.world.entity.spec import EntitySpec, PLAYER_ENTITY_SPEC, ITEM_ENTITY_SPEC


class Entity:

    def __init__(self, spec: EntitySpec, entity_unique_id: EntityUniqueID, entity_runtime_id: EntityRuntimeID) -> None:
        self._spec = spec
        self._entity_unique_id = entity_unique_id
        self._entity_runtime_id = entity_runtime_id
        self._spawn_position = Vector3(256, 56, 256)
        self._position = Vector3(0.0, 0.0, 0.0)
        self._pitch = 0.0
        self._yaw = 0.0
        self._head_yaw = 0.0
        self._on_ground = True

    def spawn(self, block_height: int) -> None:
        y = self._spawn_position.y if self._spawn_position.y > block_height else block_height
        self.position = self._spawn_position.copy(
            x=self._spawn_position.x + 0.5,
            y=y + self._spec.eye_height,
            z=self._spawn_position.z + 0.5
        )

    @property
    def entity_unique_id(self) -> EntityUniqueID:
        return self._entity_unique_id

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        return self._entity_runtime_id

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

    @property
    def head_yaw(self) -> float:
        return self._head_yaw

    @head_yaw.setter
    def head_yaw(self, value: float) -> None:
        self._head_yaw = value

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool) -> None:
        self._on_ground = value

    @property
    def obb(self) -> OrientedBoundingBox:
        return OrientedBoundingBox.create(
            self.position.copy(y=self.position.y - self._spec.eye_height),
            self._spec.size,
            self._yaw
        )

    def is_hit_by(self, other: 'Entity') -> bool:
        return self.obb.has_collision(other.obb)


class PlayerEntity(Entity):

    def __init__(self, player_id: PlayerID, entity_unique_id: EntityUniqueID, entity_runtime_id: EntityRuntimeID) -> None:
        super().__init__(PLAYER_ENTITY_SPEC, entity_unique_id, entity_runtime_id)
        self._player_id = player_id
        self._health = 20.0
        self._hunger = 20.0
        self._inventory = MutableInventory(WindowType.INVENTORY)
        self._armor = MutableInventory(WindowType.ARMOR)

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

    def get_inventory(self, window_type: WindowType) -> Inventory:
        if window_type == WindowType.CREATIVE:
            return Inventory(window_type, INVENTORY_CONTENT_ITEMS121)
        if window_type == WindowType.INVENTORY:
            return self._inventory.to_value()
        if window_type == WindowType.ARMOR:
            return self._armor.to_value()
        raise AssertionError(window_type)

    def append_to_inventory(self, item: Slot) -> int:
        return self._inventory.append(item)


class ItemEntity(Entity):

    def __init__(self, item: Slot, entity_unique_id: EntityUniqueID, entity_runtime_id: EntityRuntimeID) -> None:
        super().__init__(ITEM_ENTITY_SPEC, entity_unique_id, entity_runtime_id)
        self._item = item

    @property
    def item(self) -> Slot:
        return self._item
