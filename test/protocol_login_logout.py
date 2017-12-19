from protocol_unconnected import UnconnectedTestCase
from testcase.protocol import *


class LoginLogoutTestCase(UnconnectedTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 58985)
    ]

    def test_login(self):
        self.test_connection_request()
        # Fragment 1/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 2/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 3/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 4/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 5/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 6/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 7/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 8/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                )
            ]
        })
        # Fragment 9/9
        received_data = self.proxy.send(self.data.that_is('login'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('login')).is_(
                    RakNetPacket(RakNetPacketType.CUSTOM_PACKET_4).that_has(
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


if __name__ == '__main__':
    import unittest
    unittest.main()