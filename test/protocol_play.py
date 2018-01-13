from protocol_login_logout import ProtocolLoginLogoutTestCase
from testcase.protocol import *


class ProtocolPlayTestCase(ProtocolLoginLogoutTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 34089)
    ]

    def setUp(self) -> None:
        super().setUp()

    def test_break_block(self):
        self.test_login()

        # start break
        self.proxy.send(self.data.that_is('break_block'), from_=self._CLIENT_ADDRESS[0])

        # breaking
        self.proxy.send(self.data.that_is('break_block'), from_=self._CLIENT_ADDRESS[0])

        # inventory transaction
        self.proxy.send(self.data.that_is('break_block'), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('break_block')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
            ]
        })

        self.proxy.next_moment()
        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('break_block')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.UPDATE_BLOCK)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.ADD_ITEM_ENTITY)
                            )
                        ),
                    )
                )
            ]
        })

        # stop break
        self.proxy.send(self.data.that_is('break_block'), from_=self._CLIENT_ADDRESS[0])

        # move
        self.proxy.send(EncodedData(self.data.that_is('take_item')).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.SOUND_EVENT),
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=2
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('take_item')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
            ]
        })

        self.proxy.next_moment()
        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('take_item')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_SLOT)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.REMOVE_ENTITY)
                            )
                        ),
                    )
                ),
            ]
        })

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('take_item')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.TAKE_ITEM_ENTITY)
                            )
                        ),
                    )
                ),
            ]
        })

        self.proxy.send(EncodedData(self.data.that_is('equipment')).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=2
                        ),
                        GamePacket(
                            GamePacketType.MOB_EQUIPMENT,
                            entity_runtime_id=2
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('equipment')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
            ]
        })

        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('equipment')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.MOB_EQUIPMENT)
                            )
                        ),
                    )
                ),
            ]
        })

    def test_put_block(self):
        self.test_break_block()

        # move
        self.proxy.send(EncodedData(self.data.that_is('put_block')).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(
                            GamePacketType.MOVE_PLAYER,
                            entity_runtime_id=2
                        )
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        # inventory transaction and mob equipment
        self.proxy.send(EncodedData(self.data.that_is('put_block')).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                    Batch().that_has(
                        GamePacket(GamePacketType.ANIMATE),
                        GamePacket(GamePacketType.ANIMATE),
                        GamePacket(GamePacketType.INVENTORY_TRANSACTION),
                        GamePacket(
                            GamePacketType.MOB_EQUIPMENT,
                            entity_runtime_id=2
                        ),
                    )
                )
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('put_block')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
            ]
        })

        self.proxy.next_moment()
        self.proxy.next_moment()
        self.proxy.next_moment()
        self.proxy.next_moment()

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('put_block')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.UPDATE_BLOCK)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.INVENTORY_SLOT)
                            )
                        ),
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            Batch().that_has(
                                GamePacket(GamePacketType.MOB_EQUIPMENT)
                            )
                        ),
                    )
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
