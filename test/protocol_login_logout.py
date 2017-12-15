from protocol_unconnected import UnconnectedTestCase


class LoginLogoutTestCase(UnconnectedTestCase):

    _CLIENT_ADDRESS = [
        ('192.168.179.2', 58985)
    ]

    def test_login(self):
        self.test_connection_request()


if __name__ == '__main__':
    import unittest
    unittest.main()
