from pyminehub.binutil.composite import *
from pyminehub.binutil.instance import *
from pyminehub.mcpe.geometry import ChunkGeometry


_layout = {
    'sub_chunk_header': 1,
    'sub_chunk_block_id': ChunkGeometry.Sub.SHAPE.volume,
    'sub_chunk_block_data': ChunkGeometry.Sub.SHAPE.volume // 2,
    'chunk_height_map': ChunkGeometry.SHAPE.area * 2,
    'chunk_biome_id': ChunkGeometry.SHAPE.area
}


class _SubChunk:
    """Chunk of ChunkGeometry.Sub.SHAPE blocks."""

    def __init__(self, header: bytes, block_id: bytes, block_data: bytes) -> None:
        assert header == b'\x00'
        self._block_id = bytearray(block_id)
        self._block_data = bytearray(block_data)

    def __iter__(self):
        yield b'\x00'
        yield bytes(self._block_id)
        yield bytes(self._block_data)


class Chunk:

    def __init__(
            self,
            sub_chunk: Sequence[_SubChunk],
            height_map: bytes,
            biome_id: bytes,
            border_block: Sequence[bytes],
            extra_data: Sequence[bytes]
    ) -> None:
        """Initialize from chunk data in packet."""
        self._sub_chunk = list(sub_chunk)
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


def create_empty_chunk() -> Chunk:
    return Chunk(
        tuple(), b'\00' * _layout['chunk_height_map'], b'\00' * _layout['chunk_biome_id'], tuple(), tuple())
