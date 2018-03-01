from typing import Optional, Tuple

from pyminehub.mcpe.const import BlockType
from pyminehub.mcpe.geometry import Face, Vector3
from pyminehub.mcpe.value import Block

__all__ = [
    'ItemSpec',
    'DefaultItemSpec',
    'DirectionalItemSpec',
    'StairItemSpec',
    'TerracottaItemSpec',
    'PumpkinSpec',
    'SlabItemSpec',
    'LadderItemSpec',
    'FenceGateItemSpec',
    'TrapDoorItemSpec',
    'DoorItemSpec',
    'BucketItemSpec',
    'FurnaceItemSpec',
    'AnvilItemSpec',
    'EndRodItemSpec',
    'LeverItemSpec',
    'ButtonItemSpec',
    'TripwireHookItemSpec',
    'StandingOrWallItemSpec',
    'TorchItemSpec',
    'ChestItemSpec'
]


class ItemSpec:

    def __init__(self, block_type: Optional[BlockType], max_quantity: int) -> None:
        self._block_type = block_type
        self._max_quantity = max_quantity

    @property
    def max_quantity(self) -> int:
        return self._max_quantity

    def to_block(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float],
            **flags: bool
    ) -> Optional[Block]:
        block_type = self.to_block_type(item_data, attached_face)
        if block_type is None or not self.is_attachable(attached_face):
            return None
        block_data = self.to_block_data(item_data, attached_face, player_yaw, click_position)
        return Block.create(block_type, block_data, **flags)

    def is_attachable(self, attached_face: Face) -> bool:
        return True

    def to_block_type(self, item_data: int, attached_facd: Face) -> Optional[BlockType]:
        return self._block_type

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        raise NotImplementedError()


class DefaultItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        return item_data


class DirectionalItemSpec(ItemSpec):

    def __init__(self, block_type: Optional[BlockType], max_quantity: int, directional_data: Tuple[int, ...]) -> None:
        super().__init__(block_type, max_quantity)
        self._directional_data = directional_data

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = DirectionalItemSpec(None, 0, (0, ))
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 0, 0, 0]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [0, 0, 0, 0]
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        8
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        8

        >>> spec = DirectionalItemSpec(None, 0, (1, 2))
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(1, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [1, 1, 1, 1]
        >>> list(spec.to_block_data(2, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 2, 2, 2]
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        0
        >>> spec.to_block_data(1, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        5
        >>> spec.to_block_data(2, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        6
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        0
        >>> spec.to_block_data(1, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        9
        >>> spec.to_block_data(2, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        10
        """
        if item_data not in self._directional_data:
            return item_data
        if attached_face in (Face.EAST, Face.WEST):
            return 4 + item_data
        if attached_face in (Face.NORTH, Face.SOUTH):
            return 8 + item_data
        return item_data


class StairItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = StairItemSpec(None, 0)
        >>> faces = [Face.WEST, Face.EAST, Face.NORTH, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [4, 5, 6, 7]
        >>> list(spec.to_block_data(0, f.inverse, f.yaw, Vector3(0.5, 0.25, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, f.inverse, f.yaw, Vector3(0.5, 0.75, 0.5)) for f in faces)
        [4, 5, 6, 7]
        """
        assert item_data == 0
        horizontal_player_face = Face.by_yaw(player_yaw)
        if attached_face is Face.TOP or (attached_face is not Face.BOTTOM and click_position.y < 0.5):
            return Face.WEST.value - horizontal_player_face.value
        else:
            return 4 + Face.WEST.value - horizontal_player_face.value


class TerracottaItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = TerracottaItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.SOUTH, Face.WEST, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, f.inverse, f.yaw, Vector3(0.5, 0.5, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.WEST, f.yaw, Vector3(1.0, 0.5, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [2, 3]
        >>> list(spec.to_block_data(0, Face.NORTH, f.yaw, Vector3(0.5, 0.5, 1.0)) for f in [Face.WEST, Face.EAST])
        [4, 5]
        >>> list(spec.to_block_data(0, Face.EAST, f.yaw, Vector3(0.0, 0.5, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [2, 3]
        >>> list(spec.to_block_data(0, Face.SOUTH, f.yaw, Vector3(0.5, 0.5, 0.0)) for f in [Face.WEST, Face.EAST])
        [4, 5]
        """
        assert item_data == 0
        horizontal_player_face = Face.by_yaw(player_yaw)
        return horizontal_player_face.inverse.value


class PumpkinSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.SOUTH: 0,
        Face.WEST: 1,
        Face.NORTH: 2,
        Face.EAST: 3
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = PumpkinSpec(None, 0)
        >>> faces = [Face.SOUTH, Face.WEST, Face.NORTH, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.EAST, f.yaw, Vector3(0.0, 0.5, 0.5)) for f in [Face.SOUTH, Face.NORTH])
        [0, 2]
        >>> list(spec.to_block_data(0, Face.WEST, f.yaw, Vector3(1.0, 0.5, 0.5)) for f in [Face.SOUTH, Face.NORTH])
        [0, 2]
        >>> list(spec.to_block_data(0, Face.SOUTH, f.yaw, Vector3(0.5, 0.5, 0.0)) for f in [Face.WEST, Face.EAST])
        [1, 3]
        >>> list(spec.to_block_data(0, Face.NORTH, f.yaw, Vector3(0.5, 0.5, 1.0)) for f in [Face.WEST, Face.EAST])
        [1, 3]
        """
        assert item_data == 0
        horizontal_player_face = Face.by_yaw(player_yaw)
        return self._FACE_TO_DATA[horizontal_player_face]


class SlabItemSpec(ItemSpec):

    _IS_UPPER = 0b1000

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = SlabItemSpec(None, 0)
        >>> y_pos = [0.0, 0.5, 1.0]
        >>> list(spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, y, 0.5)) for y in y_pos)
        [0, 8, 0]
        >>> list(spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, y, 0.5)) for y in y_pos)
        [0, 8, 0]
        >>> list(spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, y, 1.0)) for y in y_pos)
        [0, 8, 0]
        >>> list(spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, y, 0.0)) for y in y_pos)
        [0, 8, 0]
        >>> list(spec.to_block_data(0, Face.TOP, Face.NORTH.yaw, Vector3(0.5, y, 0.5)) for y in [0.5, 1.0])
        [8, 0]
        >>> list(spec.to_block_data(0, Face.BOTTOM, Face.NORTH.yaw, Vector3(0.5, y, 0.5)) for y in [0.0, 0.5])
        [8, 0]
        >>> list(spec.to_block_data(1, Face.BOTTOM, Face.NORTH.yaw, Vector3(0.5, y, 0.5)) for y in [0.0, 0.5])
        [9, 1]
        """
        assert not (attached_face is Face.TOP and click_position.y == 0.0)
        assert not (attached_face is Face.BOTTOM and click_position.y == 1.0)
        y = click_position.y % 1.0
        if attached_face is Face.BOTTOM:
            return item_data | (self._IS_UPPER if y < 0.5 else 0)
        else:
            return item_data | (self._IS_UPPER if y >= 0.5 else 0)


class LadderItemSpec(ItemSpec):

    def is_attachable(self, attached_face: Face) -> bool:
        return attached_face not in (Face.TOP, Face.BOTTOM)

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = LadderItemSpec(None, 0)
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        5
        """
        assert attached_face not in (Face.TOP, Face.BOTTOM)
        return attached_face.value


class FenceGateItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.NORTH: 0,
        Face.EAST: 1,
        Face.SOUTH: 2,
        Face.WEST: 3
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = FenceGateItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.EAST, Face.SOUTH, Face.WEST]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        return self._FACE_TO_DATA[horizontal_player_face]


class TrapDoorItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.EAST: 0,
        Face.WEST: 1,
        Face.SOUTH: 2,
        Face.NORTH: 3
    }

    _IS_UPPER = 0b100

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = TrapDoorItemSpec(None, 0)
        >>> faces = [Face.EAST, Face.WEST, Face.SOUTH, Face.NORTH]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [4, 5, 6, 7]
        >>> list(spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, y, 0.5)) for y in [0.0, 0.5])
        [0, 4]
        >>> list(spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, y, 0.5)) for y in [0.0, 0.5])
        [1, 5]
        >>> list(spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, y, 1.0)) for y in [0.0, 0.5])
        [2, 6]
        >>> list(spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, y, 0.0)) for y in [0.0, 0.5])
        [3, 7]
        """
        assert not (attached_face is Face.TOP and click_position.y == 0.0)
        assert not (attached_face is Face.BOTTOM and click_position.y == 1.0)
        horizontal_player_face = Face.by_yaw(player_yaw)
        y = click_position.y % 1.0
        is_upper = self._IS_UPPER if y >= 0.5 or attached_face is Face.BOTTOM else 0
        return self._FACE_TO_DATA[horizontal_player_face] | is_upper


class DoorItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.WEST: 0,
        Face.NORTH: 1,
        Face.EAST: 2,
        Face.SOUTH: 3
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = DoorItemSpec(None, 0)
        >>> faces = [Face.WEST, Face.NORTH, Face.EAST, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        return self._FACE_TO_DATA[horizontal_player_face]


class BucketItemSpec(ItemSpec):

    _TO_BLOCK_TYPE = {
        8: BlockType.FLOWING_WATER,
        10: BlockType.FLOWING_LAVA
    }

    def __init__(self) -> None:
        super().__init__(None, 1)

    def to_block_type(self, item_data: int, attached_face: Face) -> Optional[BlockType]:
        """
        >>> spec = BucketItemSpec()
        >>> spec.to_block_type(8, Face.NONE)
        <BlockType.FLOWING_WATER: 8>
        >>> spec.to_block_type(10, Face.NONE)
        <BlockType.FLOWING_LAVA: 10>
        >>> spec.to_block_type(0, Face.NONE)
        >>> spec.to_block_type(1, Face.NONE)
        """
        return self._TO_BLOCK_TYPE.get(item_data, None)

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        return 0


class FurnaceItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.NORTH: 2,
        Face.SOUTH: 3,
        Face.WEST: 4,
        Face.EAST: 5
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = FurnaceItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.SOUTH, Face.WEST, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        5
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        return self._FACE_TO_DATA[horizontal_player_face]


class AnvilItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.WEST: 0,
        Face.NORTH: 1,
        Face.EAST: 2,
        Face.SOUTH: 3
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = AnvilItemSpec(None, 0)
        >>> faces = [Face.WEST, Face.NORTH, Face.EAST, Face.SOUTH]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [0, 1, 2, 3]
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        return self._FACE_TO_DATA[horizontal_player_face]


class EndRodItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.BOTTOM: 0,
        Face.TOP: 1,
        Face.NORTH: 2,
        Face.SOUTH: 3,
        Face.WEST: 4,
        Face.EAST: 5
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = EndRodItemSpec(None, 0)
        >>> spec.to_block_data(0, Face.BOTTOM, Face.NORTH.yaw, Vector3(0.5, 0.0, 0.5))
        0
        >>> spec.to_block_data(0, Face.TOP, Face.NORTH.yaw, Vector3(0.5, 0.0, 0.5))
        1
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        2
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        3
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        5
        """
        return self._FACE_TO_DATA[attached_face]


class LeverItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.WEST: 1,
        Face.EAST: 2,
        Face.NORTH: 3,
        Face.SOUTH: 4
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = LeverItemSpec(None, 0)
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in [Face.EAST, Face.WEST])
        [0, 0]
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        1
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        4
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [5, 5]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in [Face.EAST, Face.WEST])
        [6, 6]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in [Face.NORTH, Face.SOUTH])
        [7, 7]
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        if attached_face is Face.TOP:
            return 5 if horizontal_player_face.direction.x == 0 else 6
        if attached_face is Face.BOTTOM:
            return 7 if horizontal_player_face.direction.x == 0 else 0
        return self._FACE_TO_DATA[attached_face]


class ButtonItemSpec(ItemSpec):

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = ButtonItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.SOUTH, Face.WEST, Face.NORTH]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [0, 0, 0, 0]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [1, 1, 1, 1]
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        5
        """
        if attached_face is Face.BOTTOM:
            return 0
        if attached_face is Face.TOP:
            return 1
        return attached_face.value


class TripwireHookItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.NORTH: 0,
        Face.EAST: 1,
        Face.SOUTH: 2,
        Face.WEST: 3
    }

    def __init__(self) -> None:
        super().__init__(BlockType.TRIPWIRE_HOOK, 64)

    def to_block_type(self, item_data: int, attached_face: Face) -> Optional[BlockType]:
        return None if attached_face in (Face.TOP, Face.BOTTOM) else BlockType.TRIPWIRE_HOOK

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = TripwireHookItemSpec()
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        0
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        1
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        3
        """
        assert attached_face not in (Face.TOP, Face.BOTTOM)
        return self._FACE_TO_DATA[attached_face]


class StandingOrWallItemSpec(ItemSpec):

    _ANGLE_UNIT = 360 // 16

    _FACE_TO_DATA = {
        Face.SOUTH: 2,
        Face.NORTH: 3,
        Face.EAST: 4,
        Face.WEST: 5
    }

    def __init__(self, standing_type: BlockType, wall_type: BlockType) -> None:
        super().__init__(None, 64)
        self._standing_type = standing_type
        self._wall_type = wall_type

    def to_block_type(self, item_data: int, attached_face: Face) -> Optional[BlockType]:
        if attached_face is Face.BOTTOM:
            return None
        if attached_face is Face.TOP:
            return self._standing_type
        return self._wall_type

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = StandingOrWallItemSpec(BlockType.STANDING_BANNER, BlockType.WALL_BANNER)
        >>> spec.to_block_data(0, Face.TOP, 180.0, Vector3(0.5, 1.0, 0.5))
        0
        >>> spec.to_block_data(0, Face.TOP, 270.0, Vector3(0.5, 1.0, 0.5))
        4
        >>> spec.to_block_data(0, Face.TOP, 360.0, Vector3(0.5, 1.0, 0.5))
        8
        >>> spec.to_block_data(0, Face.TOP, 90.0, Vector3(0.5, 1.0, 0.5))
        12
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(0.0, 0.5, 0.5))
        5
        """
        assert attached_face is not Face.BOTTOM
        if attached_face is Face.TOP:
            return int(player_yaw + 180) // self._ANGLE_UNIT % 16
        else:
            return self._FACE_TO_DATA[attached_face]


class TorchItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.TOP: 0,
        Face.WEST: 1,
        Face.EAST: 2,
        Face.NORTH: 3,
        Face.SOUTH: 4
    }

    def to_block_type(self, item_data: int, attached_facd: Face) -> Optional[BlockType]:
        return None if attached_facd is Face.BOTTOM else super().to_block_type(item_data, attached_facd)

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = TorchItemSpec(None, 0)
        >>> spec.to_block_data(0, Face.TOP, Face.NORTH.yaw, Vector3(0.5, 1.0, 0.5))
        0
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        1
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        4
        """
        assert attached_face is not Face.BOTTOM
        return self._FACE_TO_DATA[attached_face]


class ChestItemSpec(ItemSpec):

    _FACE_TO_DATA = {
        Face.NORTH: 2,
        Face.SOUTH: 3,
        Face.WEST: 4,
        Face.EAST: 5
    }

    def to_block_data(
            self,
            item_data: int,
            attached_face: Face,
            player_yaw: float,
            click_position: Vector3[float]
    ) -> int:
        """
        >>> spec = ChestItemSpec(None, 0)
        >>> faces = [Face.NORTH, Face.SOUTH, Face.WEST, Face.EAST]
        >>> list(spec.to_block_data(0, Face.TOP, f.yaw, Vector3(0.5, 1.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> list(spec.to_block_data(0, Face.BOTTOM, f.yaw, Vector3(0.5, 0.0, 0.5)) for f in faces)
        [2, 3, 4, 5]
        >>> spec.to_block_data(0, Face.SOUTH, Face.NORTH.yaw, Vector3(0.5, 0.5, 0.0))
        2
        >>> spec.to_block_data(0, Face.NORTH, Face.SOUTH.yaw, Vector3(0.5, 0.5, 1.0))
        3
        >>> spec.to_block_data(0, Face.EAST, Face.WEST.yaw, Vector3(0.0, 0.5, 0.5))
        4
        >>> spec.to_block_data(0, Face.WEST, Face.EAST.yaw, Vector3(1.0, 0.5, 0.5))
        5
        """
        horizontal_player_face = Face.by_yaw(player_yaw)
        if attached_face in (Face.TOP, Face.BOTTOM):
            return self._FACE_TO_DATA[horizontal_player_face]
        else:
            return self._FACE_TO_DATA[attached_face.inverse]


if __name__ == '__main__':
    import doctest
    doctest_result = doctest.testmod()
