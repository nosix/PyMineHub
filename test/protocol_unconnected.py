from testcase.protocol import *


class UnconnectedTestCase(ProtocolTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 44457)
    ]

    def test_unconnected_ping_pong(self):
        receieved_data = self.proxy.send(
            self._CLIENT_ADDRESS[0],
            '0100000000003c7b8400ffff00fefefefefdfdfdfd123456789c662df309da12'
            '60')
        self.assert_that(receieved_data, {
            self._CLIENT_ADDRESS[0]: [
                EncodedData(
                    '1c00000000003c7b842bf5b4544c75f13d00ffff00fefefefefdfdfdfd123456'
                    '7800544d4350453b506f636b65744d696e652d4d50205365727665723b313431'
                    '3b312e322e353b303b32303b333136373633363138373037383036323339373b'
                    '506f636b65744d696e652d4d503b537572766976616c3b'
                ).is_(
                    RakNetPacket(
                        server_guid=472877960873915066,
                        server_id='MCPE;Steve;137;1.2.3;1;5;472877960873915065;testWorld;Survival;')
                )
            ]
        })


if __name__ == '__main__':
    import unittest
    unittest.main()
