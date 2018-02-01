import world_creative
from pyminehub.mcpe.action import ActionType
from pyminehub.mcpe.const import *
from pyminehub.mcpe.event import event_factory, EventType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.value import *


class WorldBlockTestCase(world_creative.WorldCreativeTestCase):

    def _equip(self, item_type: ItemType, item_data: int) -> Item:
        item = Item.create(item_type, 64, item_data)

        self.perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            item=item
        )
        self.perform_action(
            ActionType.SET_INVENTORY,
            entity_runtime_id=1,
            inventory_slot=0,
            item=item
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            equipped_item=item
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self.get_player_id(0),
            inventory_slot=0,
            slot_item=item
        )
        self.assertEqual(expected_event, actual_event)

        return item

    def _put_item(self, position: Vector3[float], click_position: Vector3[float], face: Face, item: Item) -> None:
        self.perform_action(
            ActionType.PUT_ITEM,
            entity_runtime_id=1,
            position=position,
            click_position=click_position,
            face=face,
            hotbar_slot=0,
            item=item
        )

    def _assert_block_updated(self, position: Vector3[float], block_type: BlockType, block_data: int) -> None:
        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.BLOCK_UPDATED,
            position=position,
            block=Block.create(block_type, block_data, neighbors=True, network=True, priority=True)
        )
        self.assertEqual(expected_event, actual_event)

    def _assert_inventory_updated(self, item: Item) -> None:
        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self.get_player_id(0),
            inventory_slot=0,
            slot_item=item
        )
        self.assertEqual(expected_event, actual_event)

    def test_put_wooden_slab(self):
        self.test_login()
        item = self._equip(ItemType.WOODEN_SLAB, 0)

        # put on top (y=62, face=TOP)
        self._put_item(Vector3(x=256, y=62, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (y=63, face=TOP)
        self._put_item(Vector3(x=256, y=63, z=257), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.PLANKS, 0)
        self._assert_inventory_updated(item)

        # put on upper (y=63, face=EAST)
        self._put_item(Vector3(x=256, y=63, z=257), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=257), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (y=62, face=TOP)
        self._put_item(Vector3(x=255, y=62, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=257), BlockType.PLANKS, 0)
        self._assert_inventory_updated(item)

        # put on top (y=63, face=TOP)
        self._put_item(Vector3(x=256, y=63, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=257), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (y=64, face=TOP)
        self._put_item(Vector3(x=256, y=64, z=257), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=257), BlockType.PLANKS, 0)
        self._assert_inventory_updated(item)

        # put on upper (y=64, face=EAST)
        self._put_item(Vector3(x=256, y=64, z=257), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=257), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (y=64, face=EAST)
        self._put_item(Vector3(x=256, y=64, z=257), Vector3(0.5, 0.0, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=257), BlockType.PLANKS, 0)
        self._assert_inventory_updated(item)

        # put on bottom (y=64, face=WEST)
        self._put_item(Vector3(x=256, y=64, z=257), Vector3(0.5, 0.0, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=257), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (y=64, face=WEST)
        self._put_item(Vector3(x=257, y=64, z=257), Vector3(0.5, 0.0, 0.5), Face.BOTTOM, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=257), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)


if __name__ == '__main__':
    import unittest
    unittest.main()
