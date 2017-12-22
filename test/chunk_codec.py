from pyminehub.mcpe.chunk import decode_chunk, encode_chunk
from testcase.chunk import ChunkTestCase


class ChunkCodecTestCase(ChunkTestCase):

    def test_chunk_01(self):
        chunk = decode_chunk(self.data)
        data = encode_chunk(chunk)
        self.assertEqual(self.data, data)


if __name__ == '__main__':
    import unittest
    unittest.main()
