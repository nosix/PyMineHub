from pyminehub.config import set_config
from testcase.protocol import *


class UnconnectedTestCase(ProtocolTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 58985)
    ]

    def setUp(self) -> None:
        set_config(server_guid=3167636187078062397)
        super().setUp()

    def test_unconnected_ping_pong(self):
        receieved_data = self.proxy.send(self.data.that_is('unconnected_ping'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(receieved_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('unconnected_ping')).is_(
                    RakNetPacket(
                        RakNetPacketID.UNCONNECTED_PONG,
                        server_id='MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;'
                    )
                )
            ]
        })

    def test_connection_request(self):
        set_config(server_guid=472877960873915066)
        received_data = self.proxy.send(self.data.that_is('raknet_connection_request_1'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('raknet_connection_request_1')).is_(
                    RakNetPacket(RakNetPacketID.OPEN_CONNECTION_REPLY1)
                )
            ]
        })
        received_data = self.proxy.send(self.data.that_is('raknet_connection_request_2'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('raknet_connection_request_2')).is_(
                    RakNetPacket(RakNetPacketID.OPEN_CONNECTION_REPLY2)
                )
            ]
        })
        received_data = self.proxy.send(self.data.that_is('connection_request'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('connection_request')).is_(
                    RakNetPacket(RakNetPacketID.CUSTOM_PACKET_4).that_has(
                        Capsule(CapsuleID.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketID.CONNECTED_PING,
                                ping_time_since_start=DYNAMIC
                            )
                        ),
                        Capsule(CapsuleID.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketID.CONNECTION_REQUEST_ACCEPTED,
                                server_time_since_start=DYNAMIC
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('connection_request')).is_(
                    RakNetPacket(RakNetPacketID.ACK)
                )
            ]
        })
        received_data = self.proxy.send(
            EncodedData(self.data.that_is('new_incoming_connection')).is_(
                RakNetPacket().that_has(
                    Capsule().that_has(
                        ConnectionPacket()
                    ),
                    Capsule().that_has(
                        ConnectionPacket(server_time_since_start=self.values['server_time_since_start'])
                    ),
                    Capsule().that_has(
                        ConnectionPacket()
                    )
                )),
            from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('new_incoming_connection')).is_(
                    RakNetPacket(RakNetPacketID.CUSTOM_PACKET_4).that_has(
                        Capsule(CapsuleID.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketID.CONNECTED_PONG,
                                pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('new_incoming_connection')).is_(
                    RakNetPacket(RakNetPacketID.ACK)
                )
            ]
        })
        received_data = self.proxy.send(self.data.that_is('connected_ping'), from_=self._CLIENT_ADDRESS[0])
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('connected_ping')).is_(
                    RakNetPacket(RakNetPacketID.CUSTOM_PACKET_4).that_has(
                        Capsule(CapsuleID.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketID.CONNECTED_PONG,
                                ping_time_since_start=DYNAMIC,
                                pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                ),
                EncodedData(self.data.that_is_response_of('connected_ping')).is_(
                    RakNetPacket(RakNetPacketID.ACK)
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
