from typing import List, Union

from pyminehub.binutil.composite import *
from pyminehub.binutil.instance import *
from pyminehub.mcpe.const import BlockType, BiomeType
from pyminehub.mcpe.geometry import ChunkGeometry, Vector3

_layout = {
    'sub_chunk_header': 1,
    'sub_chunk_block_id': ChunkGeometry.Sub.SHAPE.volume,
    'sub_chunk_block_data': ChunkGeometry.Sub.SHAPE.volume // 2,
    'chunk_height_map': ChunkGeometry.SHAPE.area * 2,
    'chunk_biome_id': ChunkGeometry.SHAPE.area
}

EMPTY_HEADER = b'\00'
EMPTY_BLOCK_ID = b'\00' * _layout['sub_chunk_block_id']
EMPTY_BLOCK_DATA = b'\00' * _layout['sub_chunk_block_data']
EMPTY_HEIGHT_MAP = b'\00' * _layout['chunk_height_map']
EMPTY_BIOME_ID = b'\00' * _layout['chunk_biome_id']


class _SubChunk:
    """Chunk of ChunkGeometry.Sub.SHAPE blocks."""

    def __init__(self, header: bytes, block_id: bytes, block_data: bytes) -> None:
        assert header == EMPTY_HEADER
        self._block_id = bytearray(block_id)
        self._block_data = bytearray(block_data)

    def __iter__(self):
        yield EMPTY_HEADER
        yield bytes(self._block_id)
        yield bytes(self._block_data)

    def copy(self) -> '_SubChunk':
        return _SubChunk(EMPTY_HEADER, self._block_id, self._block_data)

    @classmethod
    def _to_block_id_index(cls, x: int, y: int, z: int) -> int:
        return (x * ChunkGeometry.SHAPE.x + z) * ChunkGeometry.SHAPE.z + y

    def get_block(self, x: int, y: int, z: int) -> BlockType:
        return BlockType(self._block_id[self._to_block_id_index(x, y, z)])

    def set_block(self, x: int, y: int, z: int, block_type: BlockType) -> None:
        self._block_id[self._to_block_id_index(x, y, z)] = block_type.value

    @classmethod
    def _to_block_data_index(cls, x: int, y: int, z: int) -> int:
        return cls._to_block_id_index(x, y, z) // 2

    def get_block_data(self, x: int, y: int, z: int) -> int:
        data = self._block_data[self._to_block_data_index(x, y, z)]
        if y & 1 == 0:
            return data & 0x0f
        else:
            return data >> 4

    def set_block_data(self, x: int, y: int, z: int, block_data: int) -> None:
        index = self._to_block_data_index(x, y, z)
        if y & 1 == 0:
            self._block_data[index] = (self._block_data[index] & 0xf0) | (block_data & 0x0f)
        else:
            self._block_data[index] = ((block_data << 4) & 0xf0) | (self._block_data[index] & 0x0f)


def _create_empty_sub_chunk() -> _SubChunk:
    return _SubChunk(EMPTY_HEADER, EMPTY_BLOCK_ID, EMPTY_BLOCK_DATA)


class Chunk:

    _Y_UNIT = ChunkGeometry.Sub.SHAPE.y  # SubChunk height

    def __init__(
            self,
            sub_chunk: Sequence[_SubChunk],
            height_map: bytes,
            biome_id: bytes,
            border_block: Sequence[bytes],
            extra_data: Sequence[bytes]
    ) -> None:
        """Initialize from chunk data in packet."""
        self._is_updated = False
        self._sub_chunk = list(sub_chunk)  # type: List[_SubChunk]
        self._height_map = bytearray(height_map)
        self._biome_id = bytearray(biome_id)
        self._border_block = list(border_block)
        self._extra_data = list(extra_data)

    def __iter__(self):
        yield tuple(self._sub_chunk)
        yield bytes(self._height_map)
        yield bytes(self._biome_id)
        yield tuple(self._border_block)
        yield tuple(self._extra_data)

    def copy(self) -> 'Chunk':
        return Chunk(
            tuple(sub_chunk.copy() for sub_chunk in self._sub_chunk),
            self._height_map, self._biome_id, self._border_block, self._extra_data)

    @property
    def is_updated(self) -> bool:
        return self._is_updated

    @is_updated.setter
    def is_updated(self, value: bool) -> None:
        self._is_updated = value

    def get_block(self, position: Vector3[int], with_data=False) -> Union[BlockType, Tuple[BlockType, int]]:
        sub_chunk_index = position.y // self._Y_UNIT
        if sub_chunk_index >= len(self._sub_chunk):
            block_type = BlockType.AIR
            if not with_data:
                return block_type
            else:
                return block_type, 0
        else:
            sub_chunk = self._sub_chunk[sub_chunk_index]
            y_in_sub = position.y % self._Y_UNIT
            block_type = sub_chunk.get_block(position.x, y_in_sub, position.z)
            if not with_data:
                return block_type
            else:
                return block_type, sub_chunk.get_block_data(position.x, y_in_sub, position.z)

    def set_block(self, position: Vector3[int], block_type: BlockType, block_data=None) -> None:
        sub_chunk_index = position.y // self._Y_UNIT
        if sub_chunk_index >= len(self._sub_chunk):
            for _ in range(sub_chunk_index - len(self._sub_chunk) + 1):
                self._sub_chunk.append(_create_empty_sub_chunk())
        sub_chunk = self._sub_chunk[sub_chunk_index]
        y_in_sub = position.y % self._Y_UNIT
        sub_chunk.set_block(position.x, y_in_sub, position.z, block_type)
        if block_data is not None:
            sub_chunk.set_block_data(position.x, y_in_sub, position.z, block_data)
        height = self.get_height(position.x, position.z)
        if position.y == height and block_type != BlockType.AIR:
            self.set_height(position.x, position.z, height + 1)
        if position.y == height - 1 and block_type == BlockType.AIR:
            self.set_height(position.x, position.z, height - 1)
        self._is_updated = True

    def get_block_data(self, position: Vector3[int]) -> int:
        sub_chunk_index = position.y // self._Y_UNIT
        if sub_chunk_index >= len(self._sub_chunk):
            return 0
        else:
            y_in_sub = position.y % self._Y_UNIT
            return self._sub_chunk[sub_chunk_index].get_block_data(position.x, y_in_sub, position.z)

    def set_block_data(self, position: Vector3[int], block_data: int) -> None:
        sub_chunk_index = position.y // self._Y_UNIT
        if sub_chunk_index >= len(self._sub_chunk):
            for _ in range(sub_chunk_index - len(self._sub_chunk) + 1):
                self._sub_chunk.append(_create_empty_sub_chunk())
        y_in_sub = position.y % self._Y_UNIT
        self._sub_chunk[sub_chunk_index].set_block_data(position.x, y_in_sub, position.z, block_data)
        self._is_updated = True

    def get_height(self, x: int, z: int) -> int:
        """Return lowest AIR height."""
        index = (x * ChunkGeometry.SHAPE.x + z) * 2
        return self._height_map[index] + (self._height_map[index + 1] << 8)

    def set_height(self, x: int, z: int, height: int) -> None:
        """Set lowest AIR height."""
        assert height >= 0
        index = (x * ChunkGeometry.SHAPE.x + z) * 2
        self._height_map[index] = height & 0xff
        self._height_map[index + 1] = height >> 8
        self._is_updated = True

    def get_biome_id(self, x: int, z: int) -> BiomeType:
        index = x * ChunkGeometry.SHAPE.x + z
        return BiomeType(self._biome_id[index])

    def set_biome_id(self, x: int, z: int, biome_type: BiomeType) -> None:
        index = x * ChunkGeometry.SHAPE.x + z
        self._biome_id[index] = biome_type.value
        self._is_updated = True


_chunk_codec_spec = (
    VarListData(BYTE_DATA, CompositeData(_SubChunk, (
        RawData(_layout['sub_chunk_header']),
        RawData(_layout['sub_chunk_block_id']),
        RawData(_layout['sub_chunk_block_data'])
    ))),
    RawData(_layout['chunk_height_map']),
    RawData(_layout['chunk_biome_id']),
    VarListData(VAR_INT_DATA, FALSE_DATA),  # TODO change FALSE_DATA
    VarListData(VAR_INT_DATA, FALSE_DATA)  # TODO change FALSE_DATA
)


_chunk_codec = CompositeCodec(_chunk_codec_spec)


def encode_chunk(chunk: Chunk) -> bytes:
    return _chunk_codec.encode(*chunk)


def decode_chunk(data: bytes) -> Chunk:
    return Chunk(*_chunk_codec.decode(data))


def foreach_xz(func: Callable[[int, int], None]) -> None:
    for x in range(ChunkGeometry.SHAPE.x):
        for z in range(ChunkGeometry.SHAPE.z):
            func(x, z)
