from protocol_unconnected import UnconnectedTestCase
from pyminehub.config import set_config
from testcase.protocol import *


class LoginLogoutTestCase(UnconnectedTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 58985)
    ]

    def setUp(self) -> None:
        set_config(seed=-1)
        super().setUp()

    def test_login(self):
        self.test_connection_request()

        # 03 Fragment 1/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 04 Fragment 2/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 05 Fragment 3/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 06 Fragment 4/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 07 Fragment 5/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 08 Fragment 6/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 09 Fragment 7/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 0a Fragment 8/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        # 0b Fragment 9/9
        self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                # 03
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.PLAY_STATUS)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.RESOURCE_PACKS_INFO)
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })

        # 0c
        self.proxy.send(
            self.data.that_is('resource_pack_client_response'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                # 04
                EncodedData(self.data.that_is_response_of('resource_pack_client_response')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.RESOURCE_PACK_STACK)
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('resource_pack_client_response')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
            ]
        })

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                # 05
                EncodedData(self.data.that_is_response_of('start_game')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            payload_length=DYNAMIC
                        ).that_has(
                            Batch().that_has(
                                GamePacket(
                                    GamePacketType.START_GAME,
                                    time=DYNAMIC,
                                    world_name='PyMineHub Server'
                                )
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.SET_TIME)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.UPDATE_ATTRIBUTES)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.AVAILABLE_COMMANDS)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.ADVENTURE_SETTINGS)
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                # 06
                EncodedData(self.data.that_is_response_of('inventory_content')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.SET_ENTITY_DATA)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_CONTENT)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_CONTENT)
                            )
                        )
                    )
                ),
                # 07
                EncodedData(self.data.that_is_response_of('inventory_content')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT)
                    )
                ),
                # 08
                EncodedData(self.data.that_is_response_of('inventory_content')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_CONTENT)
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                # 09
                EncodedData(self.data.that_is_response_of('some_data')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.MOB_EQUIPMENT)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_SLOT)
                            )
                        )
                    )
                ),
                # 0a
                EncodedData(self.data.that_is_response_of('some_data')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT)
                    )
                ),
                # 0b
                EncodedData(self.data.that_is_response_of('some_data')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.PLAYER_LIST)
                            )
                        )
                    )
                ),
                # 0c-1b
                *[
                    EncodedData(self.data.that_is_response_of('some_data')).is_(
                        RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                            RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT)
                        ).with_label(by_index(0x0c, i))
                    )
                    for i in range(16)
                ],
                # 1c
                EncodedData(self.data.that_is_response_of('some_data')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED_HAS_SPLIT).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.CRAFTING_DATA)
                            )
                        ),
                    )
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
