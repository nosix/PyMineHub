from pyminehub.config import set_config
from testcase.protocol import *


class UnconnectedTestCase(ProtocolTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 34089)
    ]

    def setUp(self) -> None:
        set_config(server_guid=1326711636852997873)
        super().setUp()

    def test_unconnected_ping_pong(self):
        self.proxy.send(self.data.that_is('unconnected_ping'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('unconnected_ping')).is_(
                    RakNetPacket(
                        RakNetPacketType.UNCONNECTED_PONG,
                        server_id='MCPE;PyMineHub Server;160;1.2.7;0;20;1326711636852997873;PyMineHub;Survival;'
                    )
                )
            ]
        })

    def test_connection_request(self):
        self.proxy.send(self.data.that_is('raknet_connection_request_1'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('raknet_connection_request_1')).is_(
                    RakNetPacket(RakNetPacketType.OPEN_CONNECTION_REPLY1)
                )
            ]
        })

        self.proxy.send(self.data.that_is('raknet_connection_request_2'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('raknet_connection_request_2')).is_(
                    RakNetPacket(RakNetPacketType.OPEN_CONNECTION_REPLY2)
                )
            ]
        })

        self.proxy.send(self.data.that_is('connection_request'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('connection_request')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
                EncodedData(self.data.that_is_response_of('connection_request')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
                                server_time_since_start=DYNAMIC
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.send(
            EncodedData(self.data.that_is('new_incoming_connection')).is_(
                RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                    RakNetFrame(RakNetFrameType.RELIABLE_ORDERED).that_has(
                        ConnectionPacket(
                            ConnectionPacketType.NEW_INCOMING_CONNECTION,
                            server_time_since_start=self.context['server_time_since_start'])
                    ),
                    RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                        ConnectionPacket(ConnectionPacketType.CONNECTED_PING)
                    )
                )),
            from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('new_incoming_connection')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
                EncodedData(self.data.that_is_response_of('new_incoming_connection')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTED_PING,
                                ping_time_since_start=DYNAMIC
                            )
                        ),
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTED_PONG,
                                pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                ),
            ]
        })

        self.proxy.send(self.data.that_is('connected_ping'), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.that_is_response_of('connected_ping')).is_(
                    RakNetPacket(RakNetPacketType.ACK)
                ),
                EncodedData(self.data.that_is_response_of('connected_ping')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4).that_has(
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTED_PONG,
                                ping_time_since_start=DYNAMIC,
                                pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
