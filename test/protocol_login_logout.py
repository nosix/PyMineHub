from protocol_unconnected import ProtocolUnconnectedTestCase
from pyminehub.mcpe.event import event_factory, EventType
from pyminehub.mcpe.resource import INVENTORY_CONTENT_ITEMS121
from pyminehub.mcpe.value import *
from testcase.protocol import *
from util.mock import CHUNK_DATA


class ProtocolLoginLogoutTestCase(ProtocolUnconnectedTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 34089)
    ]

    def setUp(self) -> None:
        super().setUp()

    def test_login(self):
        self.test_connection_request()

        for i in range(8):
            packet_type = RakNetPacketType.FRAME_SET_4 if i == 0 else RakNetPacketType.FRAME_SET_C
            self.proxy.send(EncodedData(self.data.that_is('login')).is_(
                RakNetPacket(packet_type, packet_sequence_num=3 + i).that_has(
                    RakNetFrame(
                        RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                        reliable_message_num=2 + i, message_ordering_index=1, message_ordering_chanel=0,
                        split_packet_count=9, split_packet_id=0, split_packet_index=i
                    )
                )
            ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.send(EncodedData(self.data.that_is('login')).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_C, packet_sequence_num=11).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                    reliable_message_num=10, message_ordering_index=1, message_ordering_chanel=0,
                    split_packet_count=9, split_packet_id=0, split_packet_index=8
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=False, packet_sequence_number_min=3, packet_sequence_number_max=11
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=3).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=1, message_ordering_index=1, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.PLAY_STATUS,
                                    status=PlayStatus.LOGIN_SUCCESS
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=2, message_ordering_index=2, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.RESOURCE_PACKS_INFO,
                                    must_accept=False,
                                    behavior_pack_entries=(),
                                    resource_pack_entries=()
                                )
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=12).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=11, message_ordering_index=2, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE,
                            status=ResourcePackStatus.HAVE_ALL_PACKS,
                            pack_ids=()
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=True, packet_sequence_number_min=12, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=4).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=3, message_ordering_index=3, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.RESOURCE_PACK_STACK,
                                    must_accept=False,
                                    behavior_pack_stack=(),
                                    resource_pack_stack=()
                                )
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.push_event(
            ActionType.LOGIN_PLAYER,
            (
                event_factory.create(
                    EventType.PLAYER_LOGGED_IN,
                    player_id=UUID('a302a666-4cac-3e3f-a6b8-685f9506f8fe'),
                    entity_unique_id=1,
                    entity_runtime_id=1,
                    game_mode=GameMode.SURVIVAL,
                    position=Vector3(256.0, 64.0, 256.0),
                    pitch=0.0,
                    yaw=358.0,
                    spawn=Vector3(512, 56, 512),
                    bed_position=Vector3(0, 0, 0),
                    permission=PlayerPermission.MEMBER,
                    attributes=(
                        Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:health'),
                        Attribute(0.0, 2048.0, 16.0, 16.0, 'minecraft:follow_range'),
                        Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:knockback_resistance'),
                        Attribute(
                            0.0, 3.4028234663852886e+38, 0.10000000149011612, 0.10000000149011612,
                            'minecraft:movement'),
                        Attribute(0.0, 3.4028234663852886e+38, 1.0, 1.0, 'minecraft:attack_damage'),
                        Attribute(0.0, 3.4028234663852886e+38, 0.0, 0.0, 'minecraft:absorption'),
                        Attribute(0.0, 20.0, 10.0, 20.0, 'minecraft:player.saturation'),
                        Attribute(0.0, 5.0, 0.8000399470329285, 0.0, 'minecraft:player.exhaustion'),
                        Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:player.hunger'),
                        Attribute(0.0, 24791.0, 0.0, 0.0, 'minecraft:player.level'),
                        Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:player.experience')
                    ),
                    metadata_flags=EntityMetaDataFlagValue.create(
                        always_show_nametag=True,
                        immobile=True,
                        swimmer=True,
                        affected_by_gravity=True,
                        fire_immune=True
                    )
                ),
                event_factory.create(
                    EventType.INVENTORY_LOADED,
                    player_id=UUID('a302a666-4cac-3e3f-a6b8-685f9506f8fe'),
                    inventory=(
                        Inventory(
                            WindowType.INVENTORY,
                            tuple(
                                Item(ItemType.AIR, None, None, None, None)
                                for _ in range(36)
                            )
                        ),
                        Inventory(
                            WindowType.ARMOR,
                            tuple(
                                Item(ItemType.AIR, None, None, None, None)
                                for _ in range(4)
                            )
                        ),
                        Inventory(WindowType.CREATIVE, INVENTORY_CONTENT_ITEMS121)
                    )
                ),
                event_factory.create(
                    EventType.SLOT_INITIALIZED,
                    player_id=UUID('a302a666-4cac-3e3f-a6b8-685f9506f8fe'),
                    inventory_slot=0,
                    hotbar_slot=0,
                    equipped_item=Item(ItemType.AIR, None, None, None, None)
                )
            )
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=13).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=12, message_ordering_index=3, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.RESOURCE_PACK_CLIENT_RESPONSE,
                            status=ResourcePackStatus.COMPLETED,
                            pack_ids=()
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()  # PLAYER_LOGGED_IN

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=True, packet_sequence_number_min=13, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=5).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=4, message_ordering_index=4, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.START_GAME,
                                    entity_unique_id=1,
                                    entity_runtime_id=1,
                                    player_game_mode=GameMode.SURVIVAL,
                                    player_position=Vector3(x=256.0, y=64.0, z=256.0),
                                    pitch=0.0,
                                    yaw=358.0,
                                    seed=0,
                                    dimension=Dimension.OVERWORLD,
                                    generator=GeneratorType.INFINITE,
                                    world_game_mode=GameMode.SURVIVAL,
                                    difficulty=Difficulty.NORMAL,
                                    spawn=Vector3(x=512, y=56, z=512),
                                    has_achievements_disabled=True,
                                    time=4800,
                                    edu_mode=False,
                                    rain_level=0.0,
                                    lightning_level=0.0,
                                    is_multi_player_game=True,
                                    has_lan_broadcast=True,
                                    has_xbox_live_broadcast=False,
                                    commands_enabled=True,
                                    is_texture_packs_required=True,
                                    game_rules=(),
                                    has_bonus_chest_enabled=False,
                                    has_start_with_map_enabled=False,
                                    has_trust_players_enabled=False,
                                    default_player_permission=PlayerPermission.MEMBER,
                                    xbox_live_broadcast_mode=0,
                                    level_id='',
                                    world_name='PyMineHub',
                                    premium_world_template_id='',
                                    unknown_bool=False,
                                    current_tick=0,
                                    enchantment_seed=0
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=5, message_ordering_index=5, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.SET_TIME, time=4800)
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=6, message_ordering_index=6, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.UPDATE_ATTRIBUTES,
                                    entity_runtime_id=1,
                                    entries=(
                                        Attribute(
                                            min=0.0, max=20.0, current=20.0, default=20.0, name='minecraft:health'),
                                        Attribute(
                                            min=0.0, max=2048.0, current=16.0, default=16.0,
                                            name='minecraft:follow_range'),
                                        Attribute(
                                            min=0.0, max=1.0, current=0.0, default=0.0,
                                            name='minecraft:knockback_resistance'),
                                        Attribute(
                                            min=0.0, max=3.4028234663852886e+38,
                                            current=0.10000000149011612,
                                            default=0.10000000149011612,
                                            name='minecraft:movement'),
                                        Attribute(
                                            min=0.0, max=3.4028234663852886e+38, current=1.0, default=1.0,
                                            name='minecraft:attack_damage'),
                                        Attribute(
                                            min=0.0, max=3.4028234663852886e+38, current=0.0, default=0.0,
                                            name='minecraft:absorption'),
                                        Attribute(
                                            min=0.0, max=20.0, current=10.0, default=20.0,
                                            name='minecraft:player.saturation'),
                                        Attribute(
                                            min=0.0, max=5.0, current=0.8000399470329285, default=0.0,
                                            name='minecraft:player.exhaustion'),
                                        Attribute(
                                            min=0.0, max=20.0, current=20.0, default=20.0,
                                            name='minecraft:player.hunger'),
                                        Attribute(
                                            min=0.0, max=24791.0, current=0.0, default=0.0,
                                            name='minecraft:player.level'),
                                        Attribute(
                                            min=0.0, max=1.0, current=0.0, default=0.0,
                                            name='minecraft:player.experience')
                                    )
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=7, message_ordering_index=7, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.SET_ENTITY_DATA,
                                    entity_runtime_id=1,
                                    metadata=(
                                        EntityMetaData(
                                            key=EntityMetaDataKey.FLAGS, type=MetaDataType.LONG, value=211106233679872),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.AIR, type=MetaDataType.SHORT, value=0),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.MAX_AIR, type=MetaDataType.SHORT, value=400),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.NAMETAG, type=MetaDataType.STRING,
                                            value='CantingAtol3766'),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.LEAD_HOLDER_EID, type=MetaDataType.LONG, value=1),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.SCALE, type=MetaDataType.FLOAT, value=1.0),
                                        EntityMetaData(
                                            key=EntityMetaDataKey.BED_POSITION, type=MetaDataType.INT_VECTOR3,
                                            value=Vector3(x=0, y=0, z=0))
                                    )
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=8, message_ordering_index=8, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.AVAILABLE_COMMANDS,
                                    enum_values=('suicide', 'pl', 'w', 'msg', 'ver', 'about'),
                                    postfixes=(),
                                    enums=(
                                        CommandEnum(name='KillAliases', index=(0,)),
                                        CommandEnum(name='PluginsAliases', index=(1,)),
                                        CommandEnum(name='TellAliases', index=(2, 3)),
                                        CommandEnum(name='VersionAliases', index=(4, 5))),
                                    command_data=(
                                        CommandData(
                                            name='ban',
                                            description='Prevents the specified player from using this server',
                                            flags=0, permission=0, aliases=-1,
                                            overloads=(
                                                (CommandParameter(name='args', type=1048593, is_optional=True),),)),
                                        CommandData(
                                            name='kill',
                                            description='Commit suicide or kill other players',
                                            flags=0, permission=0, aliases=0,
                                            overloads=(
                                                (CommandParameter(name='args', type=1048593, is_optional=True),),)),
                                        CommandData(
                                            name='plugins',
                                            description='Gets a list of plugins running on the server',
                                            flags=0, permission=0, aliases=1,
                                            overloads=(
                                                (CommandParameter(name='args', type=1048593, is_optional=True),),)),
                                        CommandData(
                                            name='tell',
                                            description='Sends a private message to the given player',
                                            flags=0, permission=0, aliases=2,
                                            overloads=(
                                                (CommandParameter(name='args', type=1048593, is_optional=True),),)),
                                        CommandData(
                                            name='version',
                                            description='Gets the version of this server including any plugins in use',
                                            flags=0, permission=0, aliases=3,
                                            overloads=(
                                                (CommandParameter(name='args', type=1048593, is_optional=True),),)),
                                    )
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=9, message_ordering_index=9, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.ADVENTURE_SETTINGS,
                                    flags=32,
                                    command_permission=CommandPermission.NORMAL,
                                    flags2=4294967295,
                                    player_permission=PlayerPermission.MEMBER,
                                    custom_flags=0,
                                    entity_unique_id=1
                                )
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.next_moment()  # INVENTORY_LOADED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=6).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=10, message_ordering_index=10, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_CONTENT,
                                    window_type=WindowType.INVENTORY,
                                    items=tuple(
                                        Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                                        for _ in range(36)
                                    )
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=11, message_ordering_index=11, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_CONTENT,
                                    window_type=WindowType.ARMOR,
                                    items=tuple(
                                        Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                                        for _ in range(4)
                                    )
                                )
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('inventory_content')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=7).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                            reliable_message_num=12, message_ordering_index=12, message_ordering_chanel=0,
                            split_packet_count=2, split_packet_id=0, split_packet_index=0
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('inventory_content')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=8).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                            reliable_message_num=13, message_ordering_index=12, message_ordering_chanel=0,
                            split_packet_count=2, split_packet_id=0, split_packet_index=1
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_CONTENT,
                                    window_type=WindowType.CREATIVE
                                    # items
                                )
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.next_moment()  # SLOT_INITIALIZED

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=9).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=14, message_ordering_index=13, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.MOB_EQUIPMENT,
                                    entity_runtime_id=1,
                                    item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None),
                                    inventory_slot=0,
                                    hotbar_slot=0,
                                    window_type=WindowType.INVENTORY
                                )
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=15, message_ordering_index=14, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.INVENTORY_SLOT,
                                    window_type=WindowType.INVENTORY,
                                    inventory_slot=0,
                                    item=Item(type=ItemType.AIR, aux_value=None, nbt=None, place_on=None, destroy=None)
                                )
                            )
                        )
                    )
                ),
                *[
                    EncodedData(self.data.that_is_response_of('crafting_data')).is_(
                        RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=10 + i).that_has(
                            RakNetFrame(
                                RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                                reliable_message_num=16 + i, message_ordering_index=15, message_ordering_chanel=0,
                                split_packet_count=17, split_packet_id=1, split_packet_index=i
                            )
                        ).with_label(by_index(0x0a, i))
                    )
                    for i in range(16)
                ],
                EncodedData(self.data.that_is_response_of('crafting_data')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=26).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT,
                            reliable_message_num=32, message_ordering_index=15, message_ordering_chanel=0,
                            split_packet_count=17, split_packet_id=1, split_packet_index=16
                        ).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.CRAFTING_DATA)
                            )
                        ),
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=33, message_ordering_index=16, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.PLAYER_LIST,
                                    list_type=PlayerListType.ADD,
                                    entries=()
                                )
                            )
                        )
                    )
                )
            ]
        })

        player_position = Vector3(256.0, 64.0, 256.0)
        required_chunk = len(tuple(to_chunk_area(player_position, 2)))
        expected_chunk_pos = tuple(p.position for p in to_chunk_area(player_position, 8))

        self.proxy.push_event(
            ActionType.REQUEST_CHUNK,
            tuple(
                event_factory.create(
                    EventType.FULL_CHUNK_LOADED,
                    position,
                    CHUNK_DATA
                )
                for position in expected_chunk_pos
            )
        )
        self.proxy.push_event(
            ActionType.REQUEST_ENTITY,
            tuple()
        )

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=14).that_has(
                RakNetFrame(
                    RakNetFrameType.RELIABLE_ORDERED,
                    reliable_message_num=13, message_ordering_index=4, message_ordering_chanel=0
                ).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.REQUEST_CHUNK_RADIUS,
                            radius=8
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=True, packet_sequence_number_min=14, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=27).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=34, message_ordering_index=17, message_ordering_chanel=0
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.CHUNK_RADIUS_UPDATED,
                                    radius=8
                                )
                            )
                        )
                    )
                )
            ]
        })

        expected_packet_sequence_num = 28
        expected_reliable_message_num = 35
        expected_message_ordering_index = 18

        for i in range(len(expected_chunk_pos)):
            self.proxy.next_moment()  # FULL_CHUNK_LOADED

            received_data = self.proxy.receive()
            if i + 1 != required_chunk:
                self.assert_that(received_data, {
                    self._CLIENT_ADDRESS[0]: [
                        EncodedData(self.data.created).is_(
                            RakNetPacket(
                                RakNetPacketType.FRAME_SET_4,
                                packet_sequence_num=expected_packet_sequence_num
                            ).that_has(
                                RakNetFrame(
                                    RakNetFrameType.RELIABLE_ORDERED,
                                    reliable_message_num=expected_reliable_message_num,
                                    message_ordering_index=expected_message_ordering_index,
                                    message_ordering_chanel=0
                                ).that_has(
                                    Batch().that_has(
                                        GamePacket(
                                            GamePacketType.FULL_CHUNK_DATA,
                                            position=expected_chunk_pos[i],
                                            data=CHUNK_DATA
                                        )
                                    )
                                )
                            ).with_label(i+1)
                        )
                    ]
                })
                expected_packet_sequence_num += 1
                expected_reliable_message_num += 1
                expected_message_ordering_index += 1
            else:
                self.assert_that(received_data, {
                    self._CLIENT_ADDRESS[0]: [
                        EncodedData(self.data.created).is_(
                            RakNetPacket(
                                RakNetPacketType.FRAME_SET_4,
                                packet_sequence_num=expected_packet_sequence_num
                            ).that_has(
                                RakNetFrame(
                                    RakNetFrameType.RELIABLE_ORDERED,
                                    reliable_message_num=expected_reliable_message_num,
                                    message_ordering_index=expected_message_ordering_index,
                                    message_ordering_chanel=0
                                ).that_has(
                                    Batch().that_has(
                                        GamePacket(
                                            GamePacketType.FULL_CHUNK_DATA,
                                            position=expected_chunk_pos[i],
                                            data=CHUNK_DATA
                                        )
                                    )
                                ),
                                RakNetFrame(
                                    RakNetFrameType.RELIABLE_ORDERED,
                                    reliable_message_num=expected_reliable_message_num + 1,
                                    message_ordering_index=expected_message_ordering_index + 1,
                                    message_ordering_chanel=0
                                ).that_has(
                                    Batch().that_has(
                                        GamePacket(
                                            GamePacketType.PLAY_STATUS,
                                            status=PlayStatus.PLAYER_SPAWN
                                        )
                                    )
                                ),
                                RakNetFrame(
                                    RakNetFrameType.RELIABLE_ORDERED,
                                    reliable_message_num=expected_reliable_message_num + 2,
                                    message_ordering_index=expected_message_ordering_index + 2,
                                    message_ordering_chanel=0
                                ).that_has(
                                    Batch().that_has(
                                        GamePacket(
                                            GamePacketType.TEXT,
                                            text_type=TextType.TRANSLATION,
                                            needs_translation=False,
                                            source=None,
                                            message='§e%multiplayer.player.joined',
                                            parameters=('CantingAtol3766', ),
                                            xbox_user_id=''
                                        )
                                    )
                                )
                            ).with_label(i+1)
                        )
                    ]
                })
                expected_packet_sequence_num += 1
                expected_reliable_message_num += 3
                expected_message_ordering_index += 3


if __name__ == '__main__':
    import unittest
    unittest.main()
