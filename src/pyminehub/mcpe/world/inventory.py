from pyminehub.mcpe.const import WindowType, ItemType
from pyminehub.mcpe.value import Item, Inventory
from pyminehub.mcpe.world.item import get_item_spec

_INVENTORY_SIZE = {
    WindowType.INVENTORY: 36,
    WindowType.ARMOR: 4
}


ITEM_AIR = Item(ItemType.AIR, None, None, None, None)


class MutableSlot:

    def __init__(self) -> None:
        self._type = ItemType.AIR
        self._quantity = 0
        self._data = None
        self._nbt = None
        self._place_on = None
        self._destroy = None

    def to_value(self) -> Item:
        if self._type == ItemType.AIR:
            return ITEM_AIR
        else:
            return Item.create(self._type, self._quantity, self._data, self._nbt, self._place_on, self._destroy)

    @property
    def is_empty(self) -> bool:
        return self._type == ItemType.AIR

    @property
    def is_full(self) -> bool:
        max_quantity = get_item_spec(self._type).max_quantity
        assert 0 <= self._quantity <= max_quantity
        return self._quantity == max_quantity

    def set(self, item: Item) -> None:
        if item.type != ItemType.AIR:
            self._type = item.type
            self._quantity = item.quantity
            self._data = item.data
            self._nbt = item.nbt
            self._place_on = item.place_on
            self._destroy = item.destroy
        else:
            self.__init__()

    def _append(self, item: Item) -> None:
        self._quantity += item.quantity

    def append(self, item: Item) -> bool:
        if self._type != ItemType.AIR and self.is_full:
            return False
        if self.is_empty:
            self.set(item)
            return True
        else:
            if self._type != item.type:
                return False
            self._append(item)
            return True

    def spend(self, item: Item) -> None:
        assert self._type == item.type, '{} == {}'.format(self._type, item.type)
        assert self._quantity == item.quantity, '{} == {}'.format(self._quantity, item.quantity)
        assert self._quantity > 0, self._quantity
        self._quantity -= 1
        if self._quantity == 0:
            self.__init__()


class MutableInventory:

    def __init__(self, window_type: WindowType)-> None:
        self._window_type = window_type
        self._slots = list(MutableSlot() for _ in range(_INVENTORY_SIZE[window_type]))

    def to_value(self) -> Inventory:
        return Inventory(self._window_type, tuple(slot.to_value() for slot in self._slots))

    def __getitem__(self, slot_index: int) -> Item:
        return self._slots[slot_index].to_value()

    def set(self, value: Inventory) -> None:
        assert value.window_type == self._window_type, '{}, {}'.format(value.window_type, self._window_type)
        assert len(value.slots) == len(self._slots), '{}, {}'.format(len(value.slots), len(self._slots))
        for slot, value in zip(self._slots, value.slots):
            slot.set(value)

    def append(self, item: Item) -> int:
        """Append item into inventory.

        :param item: appended item
        :return: index of the slot appended
        """
        for i, slot in enumerate(self._slots):
            if slot.append(item):
                return i
        raise AssertionError('{} can not be appended.'.format(item))

    def spend(self, slot_index: int, item: Item) -> Item:
        slot = self._slots[slot_index]
        slot.spend(item)
        return slot.to_value()
