from pyminehub.mcpe.const import WindowType, ItemType
from pyminehub.mcpe.value import Item, Inventory


_INVENTORY_SIZE = {
    WindowType.INVENTORY: 36,
    WindowType.ARMOR: 4
}


class MutableSlot:

    def __init__(self) -> None:
        self._type = ItemType.AIR
        self._aux_value = None
        self._nbt = None
        self._place_on = None
        self._destroy = None

    def to_value(self) -> Item:
        return Item(self._type, self._aux_value, self._nbt, self._place_on, self._destroy)

    def set(self, item: Item) -> None:
        self._type = item.type
        self._aux_value = item.aux_value
        self._nbt = item.nbt
        self._place_on = item.place_on
        self._destroy = item.destroy


class MutableInventory:

    def __init__(self, window_type: WindowType)-> None:
        self._window_type = window_type
        self._slots = list(MutableSlot() for _ in range(_INVENTORY_SIZE[window_type]))
        self._selected = 0

    def to_value(self) -> Inventory:
        return Inventory(self._window_type, tuple(slot.to_value() for slot in self._slots))

    def append(self, item: Item) -> int:
        self._slots[self._selected].set(item)
        return self._selected
