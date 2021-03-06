from typing import Callable, List, Optional, Tuple

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.action import Action
from pyminehub.mcpe.const import HOTBAR_SIZE, WindowType, EntityType
from pyminehub.mcpe.geometry import Vector3, OrientedBoundingBox
from pyminehub.mcpe.resource import INVENTORY_CONTENT_ITEMS121
from pyminehub.mcpe.value import EntityUniqueID, EntityRuntimeID, PlayerID, Inventory, Item, Hotbar
from pyminehub.mcpe.world.entity.spec import EntitySpec, PLAYER_ENTITY_SPEC, ITEM_ENTITY_SPEC, get_spec
from pyminehub.mcpe.world.inventory import ITEM_AIR, MutableInventory

__all__ = [
    'Entity',
    'PlayerEntity',
    'ItemEntity',
    'MobEntity'
]


class Entity:

    def __init__(self, spec: EntitySpec, entity_unique_id: EntityUniqueID, entity_runtime_id: EntityRuntimeID) -> None:
        self._spec = spec
        self._entity_unique_id = entity_unique_id
        self._entity_runtime_id = entity_runtime_id
        self._spawn_position = Vector3(*get_value(ConfigKey.PLAYER_SPAWN_POSITION))
        self._position = None
        self._pitch = 0.0
        self._yaw = 0.0
        self._head_yaw = 0.0
        self._on_ground = True
        self._move_actions = []  # type: List[Action]

    def spawn(self, block_height: int) -> None:
        assert self._position is None
        y = self._spawn_position.y if self._spawn_position.y > block_height else block_height
        self.position = self._spawn_position.copy(
            x=self._spawn_position.x + 0.5,
            y=y + self._spec.position_height,
            z=self._spawn_position.z + 0.5
        )

    @property
    def is_living(self) -> bool:
        return self._position is not None

    @property
    def entity_unique_id(self) -> EntityUniqueID:
        return self._entity_unique_id

    @property
    def entity_runtime_id(self) -> EntityRuntimeID:
        return self._entity_runtime_id

    @property
    def spawn_position(self) -> Vector3[int]:
        return self._spawn_position

    @spawn_position.setter
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
            self.position - (0, self._spec.position_height, 0),
            self._spec.size,
            self._yaw
        )

    @property
    def has_move_action(self) -> bool:
        return len(self._move_actions) > 0

    def push_move_action(self, action: Action) -> None:
        self._move_actions.append(action)

    def pop_move_action(self) -> Action:
        return self._move_actions.pop(0)

    def is_hit_by(self, other: 'Entity') -> bool:
        return self.obb.has_collision(other.obb)

    def move(
            self,
            position: Vector3[float],
            revise_position: Callable[[OrientedBoundingBox, bool], Vector3[float]]
    ) -> None:
        oob = OrientedBoundingBox.create(
            position - (0, self._spec.position_height, 0),
            self._spec.size,
            self._yaw
        )
        self.position = revise_position(oob, self.on_ground) + (0, self._spec.position_height, 0)


class PlayerEntity(Entity):

    def __init__(
            self,
            player_id: PlayerID,
            entity_unique_id: EntityUniqueID,
            entity_runtime_id: EntityRuntimeID,
            is_guest: bool
    ) -> None:
        super().__init__(PLAYER_ENTITY_SPEC, entity_unique_id, entity_runtime_id)
        self._player_id = player_id
        self._is_guest = is_guest
        self._health = 20.0
        self._hunger = 20.0
        self._air = 0.0
        self._inventory = MutableInventory(WindowType.INVENTORY)
        self._armor = MutableInventory(WindowType.ARMOR)
        self._hotbar_to_inventory = [None] * HOTBAR_SIZE  # type: List[Optional[int]]
        self._selected_hotbar_slot = 0

    @property
    def player_id(self) -> PlayerID:
        return self._player_id

    @property
    def is_guest(self) -> bool:
        return self._is_guest

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

    @property
    def air(self) -> float:
        return self._air

    @air.setter
    def air(self, value: float) -> None:
        self._air = value

    @property
    def hotbar_slot(self) -> int:
        return self._selected_hotbar_slot

    @hotbar_slot.setter
    def hotbar_slot(self, value: int) -> None:
        self._selected_hotbar_slot = value

    @property
    def hotbar(self) -> Hotbar:
        return tuple(self._hotbar_to_inventory)

    @hotbar.setter
    def hotbar(self, hotbar: Hotbar) -> None:
        assert len(hotbar) == len(self._hotbar_to_inventory)
        for i, slot in enumerate(hotbar):
            self._hotbar_to_inventory[i] = slot

    @property
    def equipped_item(self) -> Item:
        inventory_slot = self.get_inventory_slot(self._selected_hotbar_slot)
        return self._inventory[inventory_slot] if inventory_slot is not None else ITEM_AIR

    def equip(self, hotbar_slot: int, inventory_slot: Optional[int]) -> None:
        self._hotbar_to_inventory[hotbar_slot] = inventory_slot
        self._selected_hotbar_slot = hotbar_slot

    def get_inventory_slot(self, hotbar_slot: int) -> Optional[int]:
        return self._hotbar_to_inventory[hotbar_slot]

    def get_inventory(self, window_type: WindowType) -> Inventory:
        if window_type == WindowType.CREATIVE:
            return Inventory(window_type, INVENTORY_CONTENT_ITEMS121)
        if window_type == WindowType.INVENTORY:
            return self._inventory.to_value()
        if window_type == WindowType.ARMOR:
            return self._armor.to_value()
        raise AssertionError(window_type)

    def set_inventory(self, window_type: WindowType, inventory: Inventory) -> None:
        if window_type == WindowType.INVENTORY:
            self._inventory.set(inventory)
        elif window_type == WindowType.ARMOR:
            self._armor.set(inventory)
        else:
            raise AssertionError(window_type)

    def get_item(self, inventory_slot: int) -> Item:
        return self._inventory[inventory_slot]

    def set_item(self, inventory_slot: int, item: Item) -> None:
        self._inventory[inventory_slot] = item

    def append_item(self, item: Item) -> int:
        return self._inventory.append(item)

    def spend_item(self, inventory_slot: int, item: Item) -> Tuple[Item, Item]:
        old_slot = self._inventory[inventory_slot]
        new_slot = self._inventory.spend(inventory_slot, item)
        return old_slot, new_slot


class ItemEntity(Entity):

    def __init__(
            self,
            item: Item,
            entity_unique_id: EntityUniqueID,
            entity_runtime_id: EntityRuntimeID
    ) -> None:
        super().__init__(ITEM_ENTITY_SPEC, entity_unique_id, entity_runtime_id)
        self._item = item

    @property
    def item(self) -> Item:
        return self._item


class MobEntity(Entity):

    def __init__(
            self,
            entity_type: EntityType,
            entity_unique_id: EntityUniqueID,
            entity_runtime_id: EntityRuntimeID
    ) -> None:
        super().__init__(get_spec(entity_type), entity_unique_id, entity_runtime_id)
        self._type = entity_type
        self._name = None

    @property
    def type(self) -> EntityType:
        return self._type

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self._name = value
