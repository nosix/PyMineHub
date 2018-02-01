import asyncio
from unittest import TestCase
from uuid import UUID, uuid4

from pyminehub.config import set_config
from pyminehub.mcpe.action import action_factory, ActionType
from pyminehub.mcpe.const import *
from pyminehub.mcpe.event import event_factory, EventType, Event
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.plugin.loader import get_plugin_loader
from pyminehub.mcpe.value import *
from pyminehub.mcpe.world import run
from util.mock import MockDataStore


class WorldCreativeTestCase(TestCase):

    def setUp(self) -> None:
        if self._testMethodName not in type(self).__dict__:
            self.skipTest('This test is defined in super class.')

        set_config(spawn_mob=False, clock_time=-4800, game_mode='CREATIVE')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._world = run(MockDataStore(), get_plugin_loader())
        self._players = []

    def tearDown(self) -> None:
        self._world.terminate()
        loop = asyncio.get_event_loop()
        try:
            pending = asyncio.Task.all_tasks()
            loop.run_until_complete(asyncio.gather(*pending))
        except asyncio.CancelledError:
            pass
        loop.close()

    def perform_action(self, action_type: ActionType, *args, **kwargs) -> None:
        self._world.perform(action_factory.create(action_type, *args, **kwargs))

    def next_event(self) -> Event:
        return asyncio.get_event_loop().run_until_complete(self._world.next_event())

    def _create_player(self, n: int) -> None:
        for _ in range(n):
            self._players.append(uuid4())

    def get_player_id(self, index: int) -> UUID:
        return self._players[index]

    def test_login(self):
        self._create_player(1)
        self.perform_action(ActionType.LOGIN_PLAYER, self.get_player_id(0))

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            player_id=self.get_player_id(0),
            entity_unique_id=1,
            entity_runtime_id=1,
            game_mode=GameMode.CREATIVE,
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
            metadata_flags=EntityMetaDataFlagValue(flags=211106233679872),
            time=4800
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self.next_event()
        self.assertEqual(4880, len(actual_event.inventory[2].slots))
        expected_event = event_factory.create(
            EventType.INVENTORY_LOADED,
            player_id=self.get_player_id(0),
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

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.SLOT_INITIALIZED,
            player_id=self.get_player_id(0),
            equipped_item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
            inventory_slot=None,
            hotbar_slot=0
        )
        self.assertEqual(expected_event, actual_event)

    def test_move_player(self):
        self.test_login()
        self.perform_action(
            ActionType.MOVE_PLAYER,
            entity_runtime_id=1,
            position=Vector3(x=257.5, y=64.625, z=254.5),
            pitch=45.0,
            yaw=60.0,
            head_yaw=30.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_MOVED,
            entity_runtime_id=1,
            position=Vector3(x=257.5, y=64.625, z=254.5),
            pitch=45.0,
            yaw=60.0,
            head_yaw=30.0,
            mode=MoveMode.NORMAL,
            on_ground=True,
            riding_eid=0
        )
        self.assertEqual(expected_event, actual_event)

    def test_break_block(self):
        self.test_login()
        self.perform_action(
            ActionType.BREAK_BLOCK,
            entity_runtime_id=1,
            position=Vector3(x=256, y=62, z=257)
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.BLOCK_UPDATED,
            position=Vector3(x=256, y=62, z=257),
            block=Block(type=BlockType.AIR, aux_value=176)
        )
        self.assertEqual(expected_event, actual_event)

    def test_equip(self):
        self.test_login()
        self.perform_action(
            ActionType.EQUIP,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )
        self.perform_action(
            ActionType.SET_INVENTORY,
            entity_runtime_id=1,
            inventory_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.EQUIPMENT_UPDATED,
            entity_runtime_id=1,
            inventory_slot=0,
            hotbar_slot=0,
            equipped_item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self.get_player_id(0),
            inventory_slot=0,
            slot_item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

    def test_put_item(self):
        self.test_equip()
        self.perform_action(
            ActionType.PUT_ITEM,
            entity_runtime_id=1,
            position=Vector3(x=256, y=61, z=257),
            click_position=Vector3(0.5, 1.0, 0.5),
            face=Face.TOP,
            hotbar_slot=0,
            item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.BLOCK_UPDATED,
            position=Vector3(x=256, y=62, z=257),
            block=Block(type=BlockType.DIRT, aux_value=176)
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.INVENTORY_UPDATED,
            player_id=self.get_player_id(0),
            inventory_slot=0,
            slot_item=Item(type=ItemType.DIRT, aux_value=64, nbt=b'', place_on=(), destroy=())
        )
        self.assertEqual(expected_event, actual_event)

    def test_logout_login(self):
        self.test_move_player()

        self.perform_action(ActionType.LOGOUT_PLAYER, 1)
        self.perform_action(ActionType.LOGIN_PLAYER, self.get_player_id(0))

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            player_id=self.get_player_id(0),
            entity_unique_id=2,
            entity_runtime_id=2,
            game_mode=GameMode.CREATIVE,
            position=Vector3(x=257.5, y=64.625, z=254.5),  # check saved value
            pitch=0.0,  # reset
            yaw=60.0,  # check saved value
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
            metadata_flags=EntityMetaDataFlagValue(flags=211106233679872),
            time=4800
        )
        self.assertEqual(expected_event, actual_event)

        actual_event = self.next_event()
        self.assertEqual(4880, len(actual_event.inventory[2].slots))
        expected_event = event_factory.create(
            EventType.INVENTORY_LOADED,
            player_id=self.get_player_id(0),
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

        actual_event = self.next_event()
        expected_event = event_factory.create(
            EventType.SLOT_INITIALIZED,
            player_id=self.get_player_id(0),
            equipped_item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
            inventory_slot=None,
            hotbar_slot=0
        )
        self.assertEqual(expected_event, actual_event)


if __name__ == '__main__':
    import unittest
    unittest.main()
