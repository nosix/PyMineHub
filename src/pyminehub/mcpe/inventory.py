from pyminehub.mcpe.const import WindowType
from pyminehub.mcpe.resource import INVENTORY_CONTENT_ITEMS121
from pyminehub.mcpe.value import Slot, Inventory

_INVENTORY_SIZE = {
    WindowType.INVENTORY: 36,
    WindowType.ARMOR: 4
}


def create_inventory(window_type: WindowType) -> Inventory:
    if window_type == WindowType.CREATIVE:
        return Inventory(window_type, INVENTORY_CONTENT_ITEMS121)
    else:
        return Inventory(
            window_type,
            tuple(Slot(0, None, None, None, None) for _ in range(_INVENTORY_SIZE[window_type])))
