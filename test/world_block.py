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

    def _move_player(self, position: Vector3[float], yaw: float) -> None:
        self.perform_action(
            ActionType.MOVE_PLAYER,
            entity_runtime_id=1,
            position=position,
            pitch=0.0,
            yaw=yaw,
            head_yaw=0.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_MOVED,
            entity_runtime_id=1,
            position=position,
            pitch=0.0,
            yaw=yaw,
            head_yaw=0.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )
        self.assertEqual(expected_event, actual_event)

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

    def _put_pole(self, position: Vector3[float], height: int, item_type: ItemType=ItemType.PLANKS) -> None:
        item = self._equip(item_type, 0)
        for h in range(height):
            self._put_item(position + (0, h, 0), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
            self._assert_block_updated(position + (0, h + 1, 0), BlockType(item_type.value), 0)
            self._assert_inventory_updated(item)

    def _break_block(self, position: Vector3[int]):
        self.perform_action(
            ActionType.BREAK_BLOCK,
            entity_runtime_id=1,
            position=position
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

        # put on top (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.DOUBLE_WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.DOUBLE_WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*TOP*, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=255, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.DOUBLE_WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*EAST*, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.DOUBLE_WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on bottom (face=WEST, block_pos=(257, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=BOTTOM, block_pos=(257, 63, 256))
        self._put_item(Vector3(x=257, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.BOTTOM, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on upper (face=SOUTH, block_pos=(256, 64, 255))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.WOODEN_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=TOP, block_pos=(256, 65, 256))
        self._put_item(Vector3(x=256, y=64, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=65, z=255), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

    def test_put_stone_slab(self):
        self.test_login()
        item = self._equip(ItemType.STONE_SLAB, 0)

        # put on top (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.DOUBLE_STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.DOUBLE_STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.STONE_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*TOP*, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=255, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.DOUBLE_STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.STONE_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*EAST*, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.DOUBLE_STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on bottom (face=WEST, block_pos=(257, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.STONE_SLAB, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=BOTTOM, block_pos=(257, 63, 256))
        self._put_item(Vector3(x=257, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.BOTTOM, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.STONE_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on upper (face=SOUTH, block_pos=(256, 64, 255))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.STONE_SLAB, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=TOP, block_pos=(256, 65, 256))
        self._put_item(Vector3(x=256, y=64, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=65, z=255), BlockType.STONE_SLAB, 0)
        self._assert_inventory_updated(item)

    def test_put_stone_slab2(self):
        self.test_login()
        item = self._equip(ItemType.STONE_SLAB2, 0)

        # put on top (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.DOUBLE_STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on slab (face=TOP, block_pos=(256, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.DOUBLE_STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.STONE_SLAB2, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*TOP*, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=255, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.DOUBLE_STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=EAST, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.STONE_SLAB2, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=*EAST*, block_pos=(255, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.DOUBLE_STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on bottom (face=WEST, block_pos=(257, 64, 256))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

        # put on upper (face=BOTTOM, block_pos=(257, 63, 256))
        self._put_item(Vector3(x=257, y=64, z=256), Vector3(0.5, 0.0, 0.5), Face.BOTTOM, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.STONE_SLAB2, 8)
        self._assert_inventory_updated(item)

        # put on upper (face=SOUTH, block_pos=(256, 64, 255))
        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.STONE_SLAB2, 8)
        self._assert_inventory_updated(item)

        # put on bottom (face=TOP, block_pos=(256, 65, 256))
        self._put_item(Vector3(x=256, y=64, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=65, z=255), BlockType.STONE_SLAB2, 0)
        self._assert_inventory_updated(item)

    def test_put_snow_layer(self):
        self.test_login()
        item = self._equip(ItemType.SNOW_LAYER, 0)

        # put on top (face=TOP, block_pos=(256, 63, 256))
        for i in range(7):
            self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
            self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.SNOW_LAYER, i)
            self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.SNOW, 0)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(256, 64, 256))
        for i in range(7):
            self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
            self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.SNOW_LAYER, i)
            self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.SNOW, 0)
        self._assert_inventory_updated(item)

        # put on side (face=EAST, block_pos=(255, 63, 256))
        for i in range(7):
            self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
            self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.SNOW_LAYER, i)
            self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.SNOW, 0)
        self._assert_inventory_updated(item)

        # put on side (face=EAST, block_pos=(255, 64, 256))
        for i in range(7):
            self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
            self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.SNOW_LAYER, i)
            self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.SNOW, 0)
        self._assert_inventory_updated(item)

    def test_put_ladder(self):
        self.test_login()
        item = self._equip(ItemType.WOODEN_SLAB, 0)

        # put a pole (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.DOUBLE_WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.WOODEN_SLAB, 0)
        self._assert_inventory_updated(item)

        item = self._equip(ItemType.LADDER, 0)

        # put on top (face=TOP, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=255, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_inventory_updated(item)

        # put on south (face=SOUTH, block_pos=(256, 63, 255))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.LADDER, 2)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_inventory_updated(item)

        # put on north (face=NORTH, block_pos=(256, 63, 257))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.LADDER, 3)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.NORTH, item)
        self._assert_inventory_updated(item)

        # put on east (face=EAST, block_pos=(255, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.LADDER, 4)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_inventory_updated(item)

        # put on west (face=WEST, block_pos=(257, 63, 256))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.LADDER, 5)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_inventory_updated(item)

    def test_put_fence_gate(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        item = self._equip(ItemType.FENCE_GATE, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._move_player(Vector3(x=256, y=63, z=254), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.FENCE_GATE, 0)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(257, 63, 256))
        self._move_player(Vector3(x=258, y=63, z=256), 90.0)  # Face.EAST
        self._put_item(Vector3(x=257, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.FENCE_GATE, 1)
        self._assert_inventory_updated(item)

        # put on top (face=SOUTH, block_pos=(256, 63, 257))
        self._move_player(Vector3(x=256, y=63, z=258), 180.0)  # Face.SOUTH
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.FENCE_GATE, 2)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=257), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.FENCE_GATE, 6)
        self._assert_inventory_updated(item)

        # put on top (face=WEST, block_pos=(255, 63, 256))
        self._move_player(Vector3(x=254, y=63, z=256), 270.0)  # Face.WEST
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.FENCE_GATE, 3)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=255, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.FENCE_GATE, 7)
        self._assert_inventory_updated(item)

    def test_put_trapdoor(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        item = self._equip(ItemType.TRAPDOOR, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._move_player(Vector3(x=256, y=63, z=254), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.TRAPDOOR, 3)
        self._assert_inventory_updated(item)

        # put on top (face=TOP, block_pos=(257, 63, 256))
        self._move_player(Vector3(x=258, y=63, z=256), 90.0)  # Face.EAST
        self._put_item(Vector3(x=257, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.TRAPDOOR, 0)
        self._assert_inventory_updated(item)

        # put on top (face=SOUTH, block_pos=(256, 63, 257))
        self._move_player(Vector3(x=256, y=63, z=258), 180.0)  # Face.SOUTH
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.0, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.TRAPDOOR, 2)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=257), BlockType.TRAPDOOR, 6)
        self._assert_inventory_updated(item)

        # put on top (face=WEST, block_pos=(255, 63, 256))
        self._move_player(Vector3(x=254, y=63, z=256), 270.0)  # Face.WEST
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.0, 0.0, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.TRAPDOOR, 1)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.TRAPDOOR, 5)
        self._assert_inventory_updated(item)

    def test_put_carpet(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        item = self._equip(ItemType.CARPET, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._move_player(Vector3(x=256, y=63, z=254), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.CARPET, 0)
        self._assert_inventory_updated(item)

        # put on top (face=SOUTH, block_pos=(256, 63, 257))
        self._move_player(Vector3(x=256, y=63, z=258), 180.0)  # Face.SOUTH
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.CARPET, 0)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_inventory_updated(item)

    def test_put_double_plant(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        self._break_block(Vector3(x=256, y=63, z=256))
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.AIR, 0)

        item = self._equip(ItemType.DOUBLE_PLANT, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.DOUBLE_PLANT, 0)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.DOUBLE_PLANT, 8)
        self._assert_inventory_updated(item)

        # can not put (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_inventory_updated(item)

    def test_break_double_plant(self):
        self.test_login()
        item = self._equip(ItemType.DOUBLE_PLANT, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.DOUBLE_PLANT, 0)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.DOUBLE_PLANT, 8)
        self._assert_inventory_updated(item)

        self._break_block(Vector3(x=256, y=63, z=255))
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.AIR, 0)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.AIR, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.DOUBLE_PLANT, 0)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.DOUBLE_PLANT, 8)
        self._assert_inventory_updated(item)

        self._break_block(Vector3(x=256, y=64, z=255))
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.AIR, 0)

    def test_put_door(self):
        self.test_login()
        item = self._equip(ItemType.WOODEN_DOOR, 0)

        # put on top (face=NORTH, block_pos=(256, 63, 258))
        self._move_player(Vector3(x=256, y=63, z=256), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=258), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_block_updated(Vector3(x=256, y=64, z=258), BlockType.WOODEN_DOOR_BLOCK, 8)  # upper flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=258), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 5)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=258), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_inventory_updated(item)

        # put on left side
        self._put_item(Vector3(x=257, y=62, z=258), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_block_updated(Vector3(x=257, y=64, z=258), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

        # put on right side
        self._put_item(Vector3(x=255, y=62, z=258), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_block_updated(Vector3(x=255, y=64, z=258), BlockType.WOODEN_DOOR_BLOCK, 9)  # right flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=255, y=63, z=258), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 5)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=255, y=64, z=258), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_inventory_updated(item)

        # put on top (face=EAST, block_pos=(254, 63, 256))
        self._move_player(Vector3(x=256, y=63, z=256), 90.0)  # Face.EAST
        self._put_item(Vector3(x=254, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 2)
        self._assert_block_updated(Vector3(x=254, y=64, z=256), BlockType.WOODEN_DOOR_BLOCK, 8)  # upper flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=254, y=63, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 6)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=254, y=64, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 2)
        self._assert_inventory_updated(item)

        # put on left side
        self._put_item(Vector3(x=254, y=62, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=257), BlockType.WOODEN_DOOR_BLOCK, 2)
        self._assert_block_updated(Vector3(x=254, y=64, z=257), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

        # put on right side
        self._put_item(Vector3(x=254, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=255), BlockType.WOODEN_DOOR_BLOCK, 2)
        self._assert_block_updated(Vector3(x=254, y=64, z=255), BlockType.WOODEN_DOOR_BLOCK, 9)  # right flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=254, y=63, z=255), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=255), BlockType.WOODEN_DOOR_BLOCK, 6)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=254, y=64, z=255), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=254, y=63, z=255), BlockType.WOODEN_DOOR_BLOCK, 2)
        self._assert_inventory_updated(item)

        # put on top (face=SOUTH, block_pos=(256, 63, 254))
        self._move_player(Vector3(x=256, y=63, z=256), 180.0)  # Face.SOUTH
        self._put_item(Vector3(x=256, y=62, z=254), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=254), BlockType.WOODEN_DOOR_BLOCK, 3)
        self._assert_block_updated(Vector3(x=256, y=64, z=254), BlockType.WOODEN_DOOR_BLOCK, 8)  # upper flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=254), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=254), BlockType.WOODEN_DOOR_BLOCK, 7)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=254), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=254), BlockType.WOODEN_DOOR_BLOCK, 3)
        self._assert_inventory_updated(item)

        # put on right side
        self._put_item(Vector3(x=257, y=62, z=254), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=254), BlockType.WOODEN_DOOR_BLOCK, 3)
        self._assert_block_updated(Vector3(x=257, y=64, z=254), BlockType.WOODEN_DOOR_BLOCK, 9)  # right flag
        self._assert_inventory_updated(item)

        # put on left side
        self._put_item(Vector3(x=255, y=62, z=254), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=254), BlockType.WOODEN_DOOR_BLOCK, 3)
        self._assert_block_updated(Vector3(x=255, y=64, z=254), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

        # put on top (face=WEST, block_pos=(258, 63, 256))
        self._move_player(Vector3(x=256, y=63, z=256), 270.0)  # Face.WEST
        self._put_item(Vector3(x=258, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=258, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 0)
        self._assert_block_updated(Vector3(x=258, y=64, z=256), BlockType.WOODEN_DOOR_BLOCK, 8)  # upper flag
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=258, y=63, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=258, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 4)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=258, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=258, y=63, z=256), BlockType.WOODEN_DOOR_BLOCK, 0)
        self._assert_inventory_updated(item)

        # put on right side
        self._move_player(Vector3(x=256, y=63, z=256), 270.0)  # Face.WEST
        self._put_item(Vector3(x=258, y=62, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=258, y=63, z=257), BlockType.WOODEN_DOOR_BLOCK, 0)
        self._assert_block_updated(Vector3(x=258, y=64, z=257), BlockType.WOODEN_DOOR_BLOCK, 9)  # right flag
        self._assert_inventory_updated(item)

        # put on left side
        self._move_player(Vector3(x=256, y=63, z=255), 270.0)  # Face.WEST
        self._put_item(Vector3(x=258, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=258, y=63, z=255), BlockType.WOODEN_DOOR_BLOCK, 0)
        self._assert_block_updated(Vector3(x=258, y=64, z=255), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

    def test_break_door(self):
        self.test_login()
        item = self._equip(ItemType.WOODEN_DOOR, 0)

        # break lower part
        self._move_player(Vector3(x=256, y=63, z=256), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=258), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_block_updated(Vector3(x=256, y=64, z=258), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

        self._break_block(Vector3(x=256, y=63, z=258))
        self._assert_block_updated(Vector3(x=256, y=64, z=258), BlockType.AIR, 0)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.AIR, 0)

        # breap upper part
        self._move_player(Vector3(x=256, y=63, z=256), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=258), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.WOODEN_DOOR_BLOCK, 1)
        self._assert_block_updated(Vector3(x=256, y=64, z=258), BlockType.WOODEN_DOOR_BLOCK, 8)
        self._assert_inventory_updated(item)

        self._break_block(Vector3(x=256, y=64, z=258))
        self._assert_block_updated(Vector3(x=256, y=64, z=258), BlockType.AIR, 0)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.AIR, 0)

    def test_put_flower_pot(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        item = self._equip(ItemType.FLOWER_POT, 0)

        # put on top (face=TOP, block_pos=(256, 63, 255))
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.FLOWER_POT_BLOCK, 0)
        self._assert_inventory_updated(item)

        # put on top (face=NORTH, block_pos=(256, 63, 257))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.FLOWER_POT_BLOCK, 0)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_inventory_updated(item)

    def test_put_end_rod(self):
        self.test_login()
        item = self._equip(ItemType.END_ROD, 0)

        # put on top (face=TOP, block_pos=(256, 63, 256))
        self._put_item(Vector3(x=256, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=256), BlockType.END_ROD, 1)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=256), BlockType.END_ROD, 0)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=65, z=256), BlockType.END_ROD, 1)
        self._assert_inventory_updated(item)

        # put on top (face=NORTH, block_pos=(256, 63, 257))
        self._put_item(Vector3(x=256, y=63, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.END_ROD, 2)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=257), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=258), BlockType.END_ROD, 3)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=63, z=258), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=259), BlockType.END_ROD, 2)
        self._assert_inventory_updated(item)

    def test_put_lever(self):
        self.test_login()
        self._put_pole(Vector3(x=256, y=62, z=256), 2)
        item = self._equip(ItemType.LEVER, 0)

        # put on SOUTH
        self._move_player(Vector3(x=256, y=63, z=254), 0.0)  # Face.NORTH
        self._put_item(Vector3(x=256, y=62, z=255), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=255), BlockType.LEVER, 5)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.LEVER, 4)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=255), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.LEVER, 12)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=255), Vector3(0.5, 0.5, 0.0), Face.SOUTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=255), BlockType.LEVER, 4)
        self._assert_inventory_updated(item)

        # put on WEST
        self._move_player(Vector3(x=258, y=63, z=256), 90.0)  # Face.EAST
        self._put_item(Vector3(x=257, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=257, y=63, z=256), BlockType.LEVER, 6)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.LEVER, 1)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=257, y=64, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.LEVER, 9)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=257, y=64, z=256), Vector3(1.0, 0.5, 0.5), Face.WEST, item)
        self._assert_block_updated(Vector3(x=257, y=64, z=256), BlockType.LEVER, 1)
        self._assert_inventory_updated(item)

        # put on NORTH
        self._move_player(Vector3(x=256, y=63, z=258), 180.0)  # Face.SOUTH
        self._put_item(Vector3(x=256, y=62, z=257), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=256, y=63, z=257), BlockType.LEVER, 5)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.5, 0.5, 1.0), Face.NORTH, item)
        self._assert_block_updated(Vector3(x=256, y=64, z=257), BlockType.LEVER, 3)
        self._assert_inventory_updated(item)

        # put on EAST
        self._move_player(Vector3(x=254, y=63, z=256), 270.0)  # Face.WEST
        self._put_item(Vector3(x=255, y=62, z=256), Vector3(0.5, 1.0, 0.5), Face.TOP, item)
        self._assert_block_updated(Vector3(x=255, y=63, z=256), BlockType.LEVER, 6)
        self._assert_inventory_updated(item)

        self._put_item(Vector3(x=256, y=64, z=256), Vector3(0.0, 0.5, 0.5), Face.EAST, item)
        self._assert_block_updated(Vector3(x=255, y=64, z=256), BlockType.LEVER, 2)
        self._assert_inventory_updated(item)


if __name__ == '__main__':
    import unittest
    unittest.main()
