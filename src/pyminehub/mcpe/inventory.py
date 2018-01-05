from pyminehub.mcpe.const import WindowType
from pyminehub.mcpe.value import Slot, Inventory


_INVENTORY_SIZE = {
    WindowType.INVENTORY: 36,
    WindowType.ARMOR: 4
}


class MutableSlot:

    def __init__(self) -> None:
        self._id = 0
        self._aux_value = None
        self._nbt = None
        self._place_on = None
        self._destroy = None

    def to_value(self) -> Slot:
        return Slot(self._id, self._aux_value, self._nbt, self._place_on, self._destroy)


class MutableInventory:

    def __init__(self, window_type: WindowType)-> None:
        self._window_type = window_type
        self._slots = list(MutableSlot() for _ in range(_INVENTORY_SIZE[window_type]))

    def to_value(self) -> Inventory:
        return Inventory(self._window_type, tuple(slot.to_value() for slot in self._slots))
