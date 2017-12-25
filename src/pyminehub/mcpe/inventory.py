from pkgutil import get_data

from pyminehub.mcpe.const import WindowType
from pyminehub.mcpe.value import Slot, Inventory

_INVENTORY_SIZE = {
    WindowType.INVENTORY: 36,
    WindowType.ARMOR: 4
}

_INVENTORY_CONTENT_ITEMS = get_data(__package__, 'inventory-content-items121.dat')


def create_inventory(window_type: WindowType) -> Inventory:
    if window_type == WindowType.CREATIVE:
        return Inventory(window_type, _INVENTORY_CONTENT_ITEMS)
    else:
        return Inventory(
            window_type,
            tuple(Slot(0, None, None, None, None) for _ in range(_INVENTORY_SIZE[window_type])))
