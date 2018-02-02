import chunk_codec
import chunk_edit
import client
import codec_extra
import codec_login_logout
import codec_play
import command
import doctestsuite
import geometry
import protocol_login_logout
import protocol_play
import protocol_unconnected
import world_block
import world_creative
import world_survival


# noinspection PyUnusedLocal
def load_tests(loader, tests, pattern):
    modules = (
        doctestsuite,
        geometry,
        command,
        chunk_codec,
        chunk_edit,
        codec_login_logout,
        codec_play,
        codec_extra,
        protocol_unconnected,
        protocol_login_logout,
        protocol_play,
        world_survival,
        world_creative,
        world_block,
        client,
    )
    suite = unittest.TestSuite()
    for m in modules:
        suite.addTests(loader.loadTestsFromModule(m))
    return suite


if __name__ == '__main__':
    import unittest
    unittest.main()
