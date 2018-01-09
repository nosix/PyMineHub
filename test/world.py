import asyncio
import uuid
from unittest import TestCase

from pyminehub.mcpe.action import action_factory, ActionType
from pyminehub.mcpe.event import event_factory, EventType, Event
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import run


class WorldTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        loop = asyncio.get_event_loop()

        def cancel_all(_loop, _context):
            tasks = asyncio.Task.all_tasks()
            for task in tasks:
                if not task.done() and not task.cancelled():
                    task.set_exception(_context['exception'])

        loop.set_exception_handler(cancel_all)

    def setUp(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._world = run(self._loop)
        self._players = []

    @classmethod
    def tearDownClass(cls) -> None:
        asyncio.get_event_loop().close()

    def _perform_action(self, action_type: ActionType, *args, **kwargs) -> None:
        self._world.perform(action_factory.create(action_type, *args, **kwargs))

    def _next_event(self) -> Event:
        return self._loop.run_until_complete(self._world.next_event())

    def _create_player(self, n: int) -> None:
        for _ in range(n):
            self._players.append(uuid.uuid4())

    def _get_player_id(self, index: int) -> UUID:
        return self._players[index]

    def test_login(self):
        self._create_player(1)
        self._perform_action(ActionType.LOGIN_PLAYER, self._get_player_id(0))

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            player_id=self._get_player_id(0),
            entity_unique_id=1,
            entity_runtime_id=1,
            game_mode=GameMode.SURVIVAL,
            position=Vector3(x=256.5, y=64.625, z=256.5),
            pitch=0.0,
            yaw=0.0,
            spawn=Vector3(x=256, y=56, z=256),
            bed_position=Vector3(x=0, y=0, z=0),
            permission=PlayerPermission.MEMBER,
            attributes=(
                Attribute(min=0.0, max=20.0, current=20.0, default=20.0, name='minecraft:health'),
                Attribute(min=0.0, max=2048.0, current=16.0, default=16.0, name='minecraft:follow_range'),
                Attribute(min=0.0, max=1.0, current=0.0, default=0.0, name='minecraft:knockback_resistance'),
                Attribute(
                    min=0.0,
                    max=3.4028234663852886e+38,
                    current=0.10000000149011612,
                    default=0.10000000149011612,
                    name='minecraft:movement'
                ),
                Attribute(
                    min=0.0,
                    max=3.4028234663852886e+38,
                    current=1.0,
                    default=1.0,
                    name='minecraft:attack_damage'
                ),
                Attribute(min=0.0, max=3.4028234663852886e+38, current=0.0, default=0.0, name='minecraft:absorption'),
                Attribute(min=0.0, max=20.0, current=10.0, default=20.0, name='minecraft:player.saturation'),
                Attribute(
                    min=0.0,
                    max=5.0,
                    current=0.8000399470329285,
                    default=0.0,
                    name='minecraft:player.exhaustion'
                ),
                Attribute(min=0.0, max=20.0, current=20.0, default=20.0, name='minecraft:player.hunger'),
                Attribute(min=0.0, max=24791.0, current=0.0, default=0.0, name='minecraft:player.level'),
                Attribute(min=0.0, max=1.0, current=0.0, default=0.0, name='minecraft:player.experience')
            ),
            metadata_flags=EntityMetaDataFlagValue(flags=211106233679872)
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        self.assertEqual(4880, len(actual_event.inventory[2].slots))
        expected_event = event_factory.create(
            EventType.INVENTORY_LOADED,
            player_id=self._get_player_id(0),
            inventory=(
                Inventory(
                    window_type=WindowType.INVENTORY,
                    slots=tuple(
                        Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                        for _ in range(36))
                ),
                Inventory(
                    window_type=WindowType.ARMOR,
                    slots=tuple(
                        Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                        for _ in range(4))
                ),
                Inventory(
                    window_type=WindowType.CREATIVE,
                    slots=actual_event.inventory[2].slots
                )
            )
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.SLOT_INITIALIZED,
            player_id=self._get_player_id(0),
            equipped_item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
            inventory_slot=0,
            hotbar_slot=0
        )
        self.assertEqual(expected_event, actual_event)

    def test_move_player(self):
        self.test_login()
        self._perform_action(
            ActionType.MOVE_PLAYER,
            entity_runtime_id=1,
            position=Vector3(x=256.5, y=64.625, z=256.5),
            pitch=0.0,
            yaw=0.0,
            head_yaw=0.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_MOVED,
            entity_runtime_id=1,
            position=Vector3(x=256.5, y=64.625, z=256.5),
            pitch=0.0,
            yaw=0.0,
            head_yaw=0.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )
        self.assertEqual(expected_event, actual_event)

    def test_break_block(self):
        self.test_login()
        self._perform_action(
            ActionType.BREAK_BLOCK,
            entity_runtime_id=1,
            position=Vector3(x=256, y=62, z=257)
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.BLOCK_UPDATED,
            position=Vector3(x=256, y=62, z=257),
            block_type=BlockType.AIR,
            block_aux=BlockData(value=176)
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.ITEM_SPAWNED,
            entity_unique_id=2,
            entity_runtime_id=2,
            item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
            position=Vector3(x=256.5, y=62.25, z=257.5),
            motion=Vector3(x=0.0, y=0.0, z=0.0),
            metadata=()
        )
        self.assertEqual(expected_event, actual_event)

    def test_item_taken(self):
        self.test_break_block()
        self._perform_action(
            ActionType.MOVE_PLAYER,
            entity_runtime_id=1,
            position=Vector3(x=256.54833984375, y=63.85153579711914, z=257.70001220703125),
            pitch=54.88166809082031,
            yaw=-1.9647674560546875,
            head_yaw=-1.9647674560546875,
            mode=MoveMode.NORMAL,
            on_ground=False,
            riding_eid=0
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self._get_player_id(0),
            inventory_slot=0,
            slot=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            slot=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.ENTITY_REMOVED,
            entity_runtime_id=2
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_MOVED,
            entity_runtime_id=1,
            position=Vector3(x=256.54833984375, y=63.85153579711914, z=257.70001220703125),
            pitch=54.88166809082031,
            yaw=-1.9647674560546875,
            head_yaw=-1.9647674560546875,
            mode=MoveMode.NORMAL,
            on_ground=False,
            riding_eid=0
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.ITEM_TAKEN,
            item_runtime_id=2,
            player_runtime_id=1
        )
        self.assertEqual(expected_event, actual_event)

        self._perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            slot=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

    def test_equip(self):
        self.test_item_taken()
        self._perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            slot=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

        self._perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=None,
            hotbar_slot=1,
            item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=None,
            hotbar_slot=1,
            slot=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
        )
        self.assertEqual(expected_event, actual_event)

    def test_put_item(self):
        self.test_item_taken()
        self._perform_action(
            ActionType.PUT_ITEM,
            entity_runtime_id=1,
            position=Vector3(x=256, y=61, z=257),
            face=Face.TOP,
            hotbar_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
        )
        self._perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=None,
            hotbar_slot=0,
            item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
        )

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.BLOCK_UPDATED,
            position=Vector3(x=256, y=62, z=257),
            block_type=BlockType.DIRT,
            block_aux=BlockData(value=176)
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self._get_player_id(0),
            inventory_slot=0,
            slot=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self._next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=None,
            hotbar_slot=0,
            slot=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
        )
        self.assertEqual(expected_event, actual_event)


if __name__ == '__main__':
    import unittest
    unittest.main()