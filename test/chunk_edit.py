from pyminehub.mcpe.chunk import decode_chunk
from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.geometry import Vector3
from testcase.chunk import ChunkTestCase


class ChunkEditTestCase(ChunkTestCase):

    def test_break_block(self):
        chunk = decode_chunk(self.data)
        base = Vector3(0, 0, 0)

        height = chunk.get_height(base.x, base.z)
        for y in range(height):
            self.assertNotEqual(BlockType.AIR, chunk.get_block(base.copy(y=y)))
        for y in range(height, 127):
            self.assertEqual(BlockType.AIR, chunk.get_block(base.copy(y=y)))

        chunk.set_block(base.copy(y=height - 1), BlockType.AIR)
        expected_height = height - 1

        height = chunk.get_height(base.x, base.z)
        self.assertEqual(expected_height, height)
        self.assertNotEqual(BlockType.AIR, chunk.get_block(base.copy(y=height - 1)))
        for y in range(height, 127):
            self.assertEqual(BlockType.AIR, chunk.get_block(base.copy(y=y)))

        chunk.set_block(base.copy(y=height - 2), BlockType.AIR)
        expected_height = height

        height = chunk.get_height(base.x, base.z)
        self.assertEqual(expected_height, height)
        self.assertNotEqual(BlockType.AIR, chunk.get_block(base.copy(y=height - 1)))
        for y in range(height, 127):
            self.assertEqual(BlockType.AIR, chunk.get_block(base.copy(y=y)))


if __name__ == '__main__':
    import unittest
    unittest.main()
