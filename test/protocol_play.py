from uuid import UUID

from protocol_login_logout import ProtocolLoginLogoutTestCase
from pyminehub.mcpe.const import *
from pyminehub.mcpe.event import event_factory, EventType
from pyminehub.mcpe.geometry import Vector3, Face
from pyminehub.mcpe.network.const import InventoryTransactionType, UseItemActionType
from pyminehub.mcpe.network.value import TransactionToUseItem
from pyminehub.mcpe.value import *
from testcase.protocol import *


class ProtocolPlayTestCase(ProtocolLoginLogoutTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 34089)
    ]

    def setUp(self) -> None:
        super().setUp()

    def test_break_block(self):
        self.test_login()

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=15).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=14, message_ordering_index=5, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.ANIMATE,
                            action_type=2, entity_runtime_id=1, unknown=None
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.START_BREAK,
                            position=Vector3(x=512, y=62, z=516),
                            face=Face.TOP
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.STOP_BREAK,
                            position=Vector3(x=1, y=4294967295, z=1),
                            face=Face.BOTTOM
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.START_BREAK,
                            position=Vector3(x=512, y=62, z=516),
                            face=Face.TOP
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.UNKNOWN_36,
                            position=Vector3(x=512, y=62, z=516),
                            face=Face.TOP
                        ),
                        GamePacket(
                            GamePacketType.SOUND_EVENT,
                            sound=SoundType.HIT,
                            position=Vector3(x=256.5, y=62.5, z=258.5),
                            extra_data=4,
                            pitch=2,
                            unknown=False,
                            disable_relative_volume=False
                        ),
                        GamePacket(
                            GamePacketType.ANIMATE,
                            action_type=2,
                            entity_runtime_id=1,
                            unknown=None
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=16).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=15, message_ordering_index=6, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.UNKNOWN_36,
                            position=Vector3(x=512, y=62, z=516),
                            face=Face.TOP
                        ),
                        GamePacket(
                            GamePacketType.SOUND_EVENT,
                            sound=SoundType.HIT,
                            position=Vector3(x=256.5, y=62.5, z=258.5),
                            extra_data=4,
                            pitch=2,
                            unknown=False,
                            disable_relative_volume=False
                        ),
                        GamePacket(
                            GamePacketType.ANIMATE,
                            action_type=2,
                            entity_runtime_id=1,
                            unknown=None
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.push_event(
            ActionType.BREAK_BLOCK,
            (
                event_factory.create(
                    EventType.BLOCK_UPDATED,
                    Vector3(x=256, y=62, z=258),
                    Block.create(BlockType.AIR, 0, neighbors=True, network=True, priority=True)
                ),
                event_factory.create(
                    EventType.ITEM_SPAWNED,
                    2,
                    2,
                    Item.create(ItemType.DIRT, 1),
                    Vector3(x=256, y=62, z=258),
                    Vector3(0.0, 0.0, 0.0),
                    tuple()
                )
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=17).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=16, message_ordering_index=7, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.UNKNOWN_36,
                            position=Vector3(x=512, y=62, z=516),
                            face=Face.TOP
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.DROP_ITEM,
                            position=Vector3(x=0, y=0, z=0),
                            face=Face.BOTTOM
                        ),
                        GamePacket(
                            GamePacketType.INVENTORY_TRANSACTION,
                            transaction_type=InventoryTransactionType.USE_ITEM,
                            actions=(),
                            data=TransactionToUseItem(
                                action_type=UseItemActionType.BREAK_BLOCK,
                                position=Vector3(x=256, y=62, z=258),
                                face=Face.TOP,
                                hotbar_slot=0,
                                item_in_hand=Item(
                                    type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
                                player_position=Vector3(x=256.5, y=64.62001037597656, z=256.5),
                                click_position=Vector3(x=0.0, y=0.0, z=0.0)
                            )
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()  # BLOCK_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=False, packet_sequence_number_min=15, packet_sequence_number_max=17
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=101).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=110, message_ordering_index=93, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.UPDATE_BLOCK,
                                    position=Vector3(x=256, y=62, z=258),
                                    block=Block(type=BlockType.AIR, aux_value=176)
                                )
                            )
                        ),
                    )
                )
            ]
        })

        self.proxy.next_moment()  # ITEM_SPAWNED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=102).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=111, message_ordering_index=94, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.ADD_ITEM_ENTITY,
                                    entity_unique_id=2,
                                    entity_runtime_id=2,
                                    item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                                    position=Vector3(x=256.0, y=62.0, z=258.0),
                                    motion=Vector3(x=0.0, y=0.0, z=0.0),
                                    metadata=()
                                )
                            )
                        ),
                    )
                )
            ]
        })

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=18).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=17, message_ordering_index=8, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.STOP_BREAK,
                            position=Vector3(x=512, y=62, z=518),
                            face=Face.BOTTOM
                        ),
                        GamePacket(
                            GamePacketType.PLAYER_ACTION,
                            entity_runtime_id=1,
                            action_type=PlayerActionType.STOP_BREAK,
                            position=Vector3(x=512, y=62, z=518),
                            face=Face.BOTTOM
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

    def test_take_item(self):
        self.test_break_block()

        self.proxy.push_event(
            ActionType.MOVE_PLAYER,
            (
                event_factory.create(
                    EventType.PLAYER_MOVED,
                    entity_runtime_id=1,
                    position=Vector3(x=256.5497741699219, y=63.62001037597656, z=258.473876953125),
                    pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                    mode=MoveMode.NORMAL,
                    on_ground=True,
                    riding_eid=0
                ),
                event_factory.create(
                    EventType.INVENTORY_UPDATED,
                    player_id=UUID('a302a666-4cac-3e3f-a6b8-685f9506f8fe'),
                    inventory_slot=0,
                    slot_item=Item.create(ItemType.DIRT, 1)
                ),
                event_factory.create(
                    EventType.ENTITY_REMOVED,
                    entity_runtime_id=3
                ),
                event_factory.create(
                    EventType.ITEM_TAKEN,
                    item_runtime_id=2,
                    player_runtime_id=1
                )
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=19).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=18, message_ordering_index=9, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.SOUND_EVENT,
                            sound=SoundType.LAND,
                            position=Vector3(x=256.54931640625, y=62.23152542114258, z=258.4552917480469),
                            extra_data=2,
                            pitch=638,
                            unknown=False,
                            disable_relative_volume=False
                        ),
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=1,
                            position=Vector3(x=256.5497741699219, y=63.62001037597656, z=258.473876953125),
                            pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                            mode=MoveMode.NORMAL,
                            on_ground=True,
                            riding_eid=0,
                            int1=None, int2=None
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()  # PLAYER_MOVED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=False, packet_sequence_number_min=18, packet_sequence_number_max=19
                    )
                ),
            ]
        })

        self.proxy.next_moment()  # INVENTORY_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=103).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=112, message_ordering_index=95, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_SLOT,
                                    inventory_slot=0,
                                    item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                                    window_type=WindowType.INVENTORY
                                )
                            )
                        ),
                    )
                ),
            ]
        })

        self.proxy.next_moment()  # ENTITY_REMOVED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=104).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=113, message_ordering_index=96, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.REMOVE_ENTITY,
                                    entity_unique_id=3
                                )
                            )
                        ),
                    )
                ),
            ]
        })

        self.proxy.next_moment()  # ITEM_TAKEN

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=105).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=114, message_ordering_index=97, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.TAKE_ITEM_ENTITY,
                                    item_runtime_id=2,
                                    player_runtime_id=1
                                )
                            )
                        ),
                    )
                ),
            ]
        })

        self.proxy.push_event(
            ActionType.MOVE_PLAYER,
            (
                event_factory.create(
                    EventType.PLAYER_MOVED,
                    entity_runtime_id=1,
                    position=Vector3(x=256.5505676269531, y=63.62001037597656, z=258.5050354003906),
                    pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                    mode=MoveMode.NORMAL,
                    on_ground=True,
                    riding_eid=0
                ),
            )
        )
        self.proxy.push_event(
            ActionType.EQUIP,
            (
                event_factory.create(
                    EventType.EQUIPMENT_UPDATED,
                    entity_runtime_id=1,
                    inventory_slot=0,
                    hotbar_slot=0,
                    equipped_item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=())
                ),
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=20).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=19, message_ordering_index=10, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=1,
                            position=Vector3(x=256.5505676269531, y=63.62001037597656, z=258.5050354003906),
                            pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                            mode=MoveMode.NORMAL,
                            on_ground=True,
                            riding_eid=0,
                            int1=None, int2=None
                        ),
                        GamePacket(
                            GamePacketType.MOB_EQUIPMENT,
                            entity_runtime_id=1,
                            item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                            inventory_slot=9,
                            hotbar_slot=0,
                            window_type=WindowType.INVENTORY
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()  # PLAYER_MOVED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=True, packet_sequence_number_min=20, packet_sequence_number_max=None
                    )
                ),
            ]
        })

        self.proxy.next_moment()  # EQUIPMENT_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=106).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=115, message_ordering_index=98, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.MOB_EQUIPMENT,
                                    entity_runtime_id=1,
                                    item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                                    inventory_slot=9,
                                    hotbar_slot=0,
                                    window_type=WindowType.INVENTORY
                                )
                            )
                        ),
                    )
                ),
            ]
        })

    def test_put_block(self):
        self.test_take_item()

        self.proxy.push_event(
            ActionType.MOVE_PLAYER,
            (
                event_factory.create(
                    EventType.PLAYER_MOVED,
                    entity_runtime_id=1,
                    position=Vector3(x=256.39129638671875, y=64.62001037597656, z=256.552001953125),
                    pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                    mode=MoveMode.NORMAL,
                    on_ground=True,
                    riding_eid=0
                ),
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=21).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=20, message_ordering_index=11, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=1,
                            position=Vector3(x=256.39129638671875, y=64.62001037597656, z=256.552001953125),
                            pitch=30.126800537109375, yaw=-1.44427490234375, head_yaw=-1.44427490234375,
                            mode=MoveMode.NORMAL,
                            on_ground=True,
                            riding_eid=0,
                            int1=None, int2=None
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.push_event(
            ActionType.PUT_ITEM,
            (
                event_factory.create(
                    EventType.BLOCK_UPDATED,
                    position=Vector3(x=256, y=62, z=258),
                    block=Block.create(BlockType.DIRT, 0, neighbors=True, network=True, priority=True)
                ),
                event_factory.create(
                    EventType.INVENTORY_UPDATED,
                    player_id=UUID('a302a666-4cac-3e3f-a6b8-685f9506f8fe'),
                    inventory_slot=0,
                    slot_item=Item.create(ItemType.AIR, 0)
                )
            )
        )
        self.proxy.push_event(
            ActionType.EQUIP,
            (
                event_factory.create(
                    EventType.EQUIPMENT_UPDATED,
                    entity_runtime_id=1,
                    inventory_slot=0,
                    hotbar_slot=0,
                    equipped_item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                ),
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=22).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=21, message_ordering_index=12, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.ANIMATE,
                            action_type=2, entity_runtime_id=1, unknown=None
                        ),
                        GamePacket(
                            GamePacketType.ANIMATE,
                            action_type=2, entity_runtime_id=1, unknown=None
                        ),
                        GamePacket(
                            GamePacketType.INVENTORY_TRANSACTION,
                            transaction_type=InventoryTransactionType.USE_ITEM,
                            actions=(
                                InventoryAction(
                                    source_type=SourceType.CONTAINER,
                                    window_type=WindowType.INVENTORY,
                                    unknown1=None,
                                    inventory_slot=0,
                                    old_item=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                                    new_item=Item(
                                        type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)),
                            ),
                            data=TransactionToUseItem(
                                action_type=UseItemActionType.CLICK_BLOCK,
                                position=Vector3(x=256, y=62, z=259),
                                face=Face.SOUTH,
                                hotbar_slot=0,
                                item_in_hand=Item(type=ItemType.DIRT, aux_value=1, nbt=b'', place_on=(), destroy=()),
                                player_position=Vector3(x=256.3912658691406, y=64.62001037597656, z=256.5500183105469),
                                click_position=Vector3(x=0.31121826171875, y=0.5553474426269531, z=0.0)
                            )
                        ),
                        GamePacket(
                            GamePacketType.MOB_EQUIPMENT,
                            entity_runtime_id=1,
                            item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
                            inventory_slot=255,
                            hotbar_slot=0,
                            window_type=WindowType.INVENTORY
                        ),
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()  # PLAYER_MOVED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=False, packet_sequence_number_min=21, packet_sequence_number_max=22
                    )
                ),
            ]
        })

        self.proxy.next_moment()  # BLOCK_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=107).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=116, message_ordering_index=99, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.UPDATE_BLOCK,
                                    position=Vector3(x=256, y=62, z=258),
                                    block=Block(type=BlockType.DIRT, aux_value=176)
                                )
                            )
                        ),
                    )
                )
            ]
        })

        self.proxy.next_moment()  # INVENTORY_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=108).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=117, message_ordering_index=100, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_SLOT,
                                    window_type=WindowType.INVENTORY,
                                    inventory_slot=0,
                                    item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                                )
                            )
                        ),
                    )
                )
            ]
        })

        self.proxy.next_moment()  # EQUIPMENT_UPDATED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=109).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=118, message_ordering_index=101, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.MOB_EQUIPMENT,
                                    entity_runtime_id=1,
                                    item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
                                    inventory_slot=9,
                                    hotbar_slot=0,
                                    window_type=WindowType.INVENTORY
                                )
                            )
                        ),
                    )
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
