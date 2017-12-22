import chunk_codec
import codec_login_logout
import doctestsuite
import protocol_login_logout
import protocol_unconnected


# noinspection PyUnusedLocal
def load_tests(loader, tests, pattern):
    modules = (
        doctestsuite,
        chunk_codec,
        codec_login_logout,
        protocol_unconnected,
        protocol_login_logout
    )
    suite = unittest.TestSuite()
    for m in modules:
        suite.addTests(loader.loadTestsFromModule(m))
    return suite


if __name__ == '__main__':
    import unittest
    unittest.main()
