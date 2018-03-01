from typing import Dict, List
from unittest import TestCase

# noinspection PyProtectedMember
from pyminehub.mcpe.block.spec import RailBlockSpec, _SURROUNDING
from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.geometry import Vector3
from pyminehub.mcpe.value import Block, PlacedBlock

AIR = Block.create(BlockType.AIR, 0)
RAIL = Block.create(BlockType.RAIL, 0)
POWERED_RAIL = Block.create(BlockType.GOLDEN_RAIL, 0)

LINKED_BLOCKS = tuple((position, AIR) for position in _SURROUNDING)


class RailTest(TestCase):

    def setUp(self):
        self.spec = RailBlockSpec(None)

    def _get_additional_blocks(self, block: Block, linked_blocks: Dict[Vector3[int], Block]) -> List[PlacedBlock]:
        linked_blocks = tuple(linked_blocks[p] for p in _SURROUNDING)
        return list(self.spec.get_additional_blocks(block, linked_blocks))

    def test_rail_0(self):
        linked_blocks = dict(LINKED_BLOCKS)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), RAIL), blocks.pop(0))

    def test_rail_1(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_rail_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 1, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=2)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 1, 0), RAIL.copy(data=1)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=2)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 1, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, -1, 0), RAIL.copy(data=2)), blocks.pop(0))

    def test_rail_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 1, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=3)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 1, 0), RAIL.copy(data=1)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=3)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 1, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, -1, 0), RAIL.copy(data=3)), blocks.pop(0))

    def test_rail_4(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, -1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, -1), RAIL.copy(data=0)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, -1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, -1), RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_rail_4(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), RAIL.copy(data=4)), blocks.pop(0))

    def test_rail_5(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, 1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, 1), RAIL.copy(data=0)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, 1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, 1), RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_rail_5(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), RAIL.copy(data=5)), blocks.pop(0))

    def test_rail_6(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=6)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=6)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_6(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, -1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), RAIL.copy(data=6)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), RAIL.copy(data=6)), blocks.pop(0))

    def test_rail_6_and_neighbour_rail_4_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=6)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, -1, 0), RAIL.copy(data=3)), blocks.pop(0))

    def test_rail_7(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=7)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=7)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_7(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, -1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), RAIL.copy(data=7)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 0, 0), RAIL.copy(data=7)), blocks.pop(0))

    def test_rail_7_and_neighbour_rail_4_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=7)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, -1, 0), RAIL.copy(data=2)), blocks.pop(0))

    def test_rail_8(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=8)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=8)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_8(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), RAIL.copy(data=8)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, -1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 0, 0), RAIL.copy(data=8)), blocks.pop(0))

    def test_rail_8_and_neighbour_rail_5_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(-1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=8)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, -1, 0), RAIL.copy(data=2)), blocks.pop(0))

    def test_rail_9(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=9)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=9)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 0, 0), RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_rail_9(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 1)] = RAIL.copy(data=1)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), RAIL.copy(data=9)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, -1)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), RAIL.copy(data=9)), blocks.pop(0))

    def test_rail_9_and_neighbour_rail_5_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = RAIL.copy(data=1)
        linked_blocks[Vector3(1, -1, 0)] = RAIL.copy(data=0)
        blocks = self._get_additional_blocks(RAIL, linked_blocks)
        self.assertEqual(3, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), RAIL.copy(data=9)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, -1, 0), RAIL.copy(data=3)), blocks.pop(0))

    def test_powered_rail_0(self):
        linked_blocks = dict(LINKED_BLOCKS)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), POWERED_RAIL), blocks.pop(0))

    def test_powered_rail_1(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_powered_rail_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 1, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=2)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 1, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=2)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, 1, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_powered_rail_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, -1, 0), POWERED_RAIL.copy(data=2)), blocks.pop(0))

    def test_powered_rail_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 1, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=3)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 1, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=3)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(-1, 1, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_neighbour_powered_rail_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(1, -1, 0), POWERED_RAIL.copy(data=3)), blocks.pop(0))

    def test_powered_rail_4(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, -1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, -1), POWERED_RAIL.copy(data=0)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, -1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=4)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, -1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_4(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), POWERED_RAIL.copy(data=4)), blocks.pop(0))

    def test_powered_rail_5(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, 1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, 1), POWERED_RAIL.copy(data=0)), blocks.pop(0))  # TODO remove

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 1, 1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=5)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 1, 1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_5(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), POWERED_RAIL.copy(data=5)), blocks.pop(0))

    def test_powered_rail_not_6(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_not_6(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, -1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_powered_rail_not_6_and_neighbour_rail_4_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), POWERED_RAIL.copy(data=4)), blocks.pop(0))

    def test_powered_rail_not_7(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_not_7(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, -1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_powered_rail_not_7_and_neighbour_rail_4_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, 1), POWERED_RAIL.copy(data=4)), blocks.pop(0))

    def test_powered_rail_not_8(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_not_8(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, 0, 1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, -1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_powered_rail_not_8_and_neighbour_rail_5_2(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(-1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), POWERED_RAIL.copy(data=5)), blocks.pop(0))

    def test_powered_rail_not_9(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, 0, -1), POWERED_RAIL.copy(data=0)), blocks.pop(0))

    def test_neighbour_powered_rail_not_9(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, 0, 1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, 0, 1)] = POWERED_RAIL.copy(data=1)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))

        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(-1, 0, 0)] = POWERED_RAIL.copy(data=0)
        linked_blocks[Vector3(-1, 0, -1)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(1, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=1)), blocks.pop(0))

    def test_powered_rail_not_9_and_neighbour_rail_5_3(self):
        linked_blocks = dict(LINKED_BLOCKS)
        linked_blocks[Vector3(0, -1, -1)] = POWERED_RAIL.copy(data=1)
        linked_blocks[Vector3(1, -1, 0)] = POWERED_RAIL.copy(data=0)
        blocks = self._get_additional_blocks(POWERED_RAIL, linked_blocks)
        self.assertEqual(2, len(blocks))
        self.assertEqual(PlacedBlock(Vector3(0, 0, 0), POWERED_RAIL.copy(data=0)), blocks.pop(0))
        self.assertEqual(PlacedBlock(Vector3(0, -1, -1), POWERED_RAIL.copy(data=5)), blocks.pop(0))


if __name__ == '__main__':
    import unittest
    unittest.main()
