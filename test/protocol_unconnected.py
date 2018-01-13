from pyminehub.config import set_config
from pyminehub.network.address import AddressInPacket
from testcase.protocol import *


class ProtocolUnconnectedTestCase(ProtocolTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 34089)
    ]

    def setUp(self) -> None:
        set_config(server_guid=1326711636852997873)
        super().setUp()

    def test_unconnected_ping_pong(self):
        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(
                RakNetPacketType.UNCONNECTED_PING,
                time_since_start=1831975, valid_message_data_id=True, client_guid=13737444287267880442
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.UNCONNECTED_PONG,
                        time_since_start=1831975, server_guid=1326711636852997873, valid_message_data_id=True,
                        server_id='MCPE;PyMineHub Server;160;1.2.7;0;20;1326711636852997873;PyMineHub;Survival;'
                    )
                )
            ]
        })

    def test_connection_request(self):
        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(
                RakNetPacketType.OPEN_CONNECTION_REQUEST1,
                valid_message_data_id=True,
                raknet_protocol_version=8,
                mtu_size=1492
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.OPEN_CONNECTION_REPLY1,
                        valid_message_data_id=True,
                        server_guid=1326711636852997873,
                        use_encryption=False,
                        mtu_size=1492
                    )
                )
            ]
        })

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(
                RakNetPacketType.OPEN_CONNECTION_REQUEST2,
                valid_message_data_id=True,
                server_address=AddressInPacket(ip_version=4, address=b'\xc0\xa8\xb3\x03', port=19132),
                mtu_size=1492,
                client_guid=10664117796461768949
            )
        ), from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.OPEN_CONNECTION_REPLY2,
                        valid_message_data_id=True,
                        server_guid=1326711636852997873,
                        client_address=AddressInPacket(ip_version=4, address=b'\xc0\xa8\xb3\x02', port=34089),
                        mtu_size=1492,
                        use_encryption=False
                    )
                )
            ]
        })

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=0).that_has(
                RakNetFrame(RakNetFrameType.RELIABLE, reliable_message_num=0).that_has(
                    ConnectionPacket(
                        ConnectionPacketType.CONNECTION_REQUEST,
                        client_guid=10664117796461768949,
                        client_time_since_start=1835755,
                        use_encryption=False
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
                        range_max_equals_to_min=True, packet_sequence_number_min=0, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.that_is_response_of('connection_request')).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=0).that_has(
                        RakNetFrame(
                            RakNetFrameType.RELIABLE_ORDERED,
                            reliable_message_num=0,
                            message_ordering_index=0, message_ordering_chanel=0
                        ).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTION_REQUEST_ACCEPTED,
                                client_address=AddressInPacket(ip_version=4, address=b'\xc0\xa8\xb3\x02', port=34089),
                                system_index=0,
                                # internal_address
                                client_time_since_start=1835755,
                                server_time_since_start=DYNAMIC,
                            )
                        )
                    )
                )
            ]
        })

        self.proxy.send(
            EncodedData(self.data.that_is('new_incoming_connection')).is_(
                RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=1).that_has(
                    RakNetFrame(
                        RakNetFrameType.RELIABLE_ORDERED,
                        reliable_message_num=1,
                        message_ordering_index=0, message_ordering_chanel=0
                    ).that_has(
                        ConnectionPacket(
                            ConnectionPacketType.NEW_INCOMING_CONNECTION,
                            server_address=AddressInPacket(ip_version=4, address=b'\xc0\xa8\xb3\x03', port=19132),
                            # internal_address
                            server_time_since_start=self.context['server_time_since_start'],
                            client_time_since_start=9992056
                        )
                    ),
                    RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                        ConnectionPacket(ConnectionPacketType.CONNECTED_PING, ping_time_since_start=9992056)
                    )
                )),
            from_=self._CLIENT_ADDRESS[0])

        received_data = self.proxy.receive()
        self.assert_that(received_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(self.data.created).is_(
                    RakNetPacket(
                        RakNetPacketType.ACK,
                        record_count=1,
                        range_max_equals_to_min=True, packet_sequence_number_min=1, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=1).that_has(
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(ConnectionPacketType.CONNECTED_PING, ping_time_since_start=DYNAMIC)
                        ),
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTED_PONG,
                                ping_time_since_start=9992056, pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                ),
            ]
        })

        self.proxy.send(EncodedData(self.data.created).is_(
            RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=2).that_has(
                RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                    ConnectionPacket(ConnectionPacketType.CONNECTED_PING, ping_time_since_start=4012048)
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
                        range_max_equals_to_min=True, packet_sequence_number_min=2, packet_sequence_number_max=None
                    )
                ),
                EncodedData(self.data.created).is_(
                    RakNetPacket(RakNetPacketType.FRAME_SET_4, packet_sequence_num=2).that_has(
                        RakNetFrame(RakNetFrameType.UNRELIABLE).that_has(
                            ConnectionPacket(
                                ConnectionPacketType.CONNECTED_PONG,
                                ping_time_since_start=4012048, pong_time_since_start=DYNAMIC
                            )
                        )
                    )
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
