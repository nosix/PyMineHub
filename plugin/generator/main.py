try:
    # noinspection PyUnresolvedReferences
    import leveldb
except ImportError:
    from generator import mock as leveldb

from enum import Enum
from pathlib import Path

from pyminehub.binutil.composite import CompositeCodec
from pyminehub.binutil.composite import NamedData
from pyminehub.binutil.converter import Endian, IntData, EnumData, OptionalData
from pyminehub.binutil.instance import BYTE_DATA
from pyminehub.mcpe.chunk import Chunk, decode_chunk, create_empty_chunk, foreach_xz
from pyminehub.mcpe.const import BlockType, BiomeType
from pyminehub.mcpe.geometry import Vector3, ChunkPosition, ChunkGeometry
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin
from pyminehub.mcpe.value import Block


class _Tag(Enum):
    DATA_2D = 45
    SUB_CHUNK = 47
    LEGACY_TERRAIN = 48
    BLOCK_ENTITY = 49
    ENTITY = 50
    VERSION = 118


class ChunkGeneratorPluginImpl(ChunkGeneratorPlugin):

    _key_codec = CompositeCodec([
        IntData(endian=Endian.LITTLE),
        IntData(endian=Endian.LITTLE),
        NamedData('tag', EnumData(BYTE_DATA, _Tag)),
        OptionalData(BYTE_DATA, lambda _context: _context['tag'] is not _Tag.SUB_CHUNK)
    ])

    _VERSION_2 = bytes([2])
    _VERSION_4 = bytes([4])

    def __init__(self) -> None:
        db_root = Path(Path(__file__).parent, 'db')
        self._db = leveldb.LevelDB(str(db_root))
        # from binascii import hexlify
        # for k, v in self._db.RangeIter():
        #     print('{}:{}'.format(hexlify(k), hexlify(v)))
        self._default_chunk = self._create_default_chunk()

    @staticmethod
    def _create_default_chunk() -> Chunk:
        def set_data(x: int, z: int) -> None:
            chunk.set_block(Vector3(x, 0, z), Block.create(BlockType.BEDROCK, 0))
            chunk.set_block(Vector3(x, 1, z), Block.create(BlockType.WATER, 0))
            chunk.set_height(x, z, 2)
            chunk.set_biome_id(x, z, BiomeType.OCEAN)
        chunk = create_empty_chunk()
        foreach_xz(set_data)
        return chunk

    def create(self, position: ChunkPosition) -> Chunk:
        key = self._key_codec.encode(position.x, position.z, _Tag.VERSION)
        try:
            version = self._db.Get(key)
            if version == self._VERSION_2:
                return self._load_version2(position)
            if version == self._VERSION_4:
                return self._load_version4(position)
        except leveldb.LevelDBError:
            pass
        return self._default_chunk

    def _load_version2(self, position: ChunkPosition) -> Chunk:
        key = self._key_codec.encode(position.x, position.z, _Tag.LEGACY_TERRAIN)
        data = self._db.Get(key)
        return decode_chunk(data, is_legacy=True)

    def _load_version4(self, position: ChunkPosition) -> Chunk:
        sub_chunks = []
        for i in range(ChunkGeometry.SHAPE.y // ChunkGeometry.Sub.SHAPE.y):
            key = self._key_codec.encode(position.x, position.z, _Tag.SUB_CHUNK, i)
            try:
                data = self._db.Get(key)
                sub_chunks.append(data)
            except KeyError:
                break
        data = bytearray()
        data.append(len(sub_chunks))
        for sub_chunk in sub_chunks:
            data += sub_chunk
        key = self._key_codec.encode(position.x, position.z, _Tag.DATA_2D)
        d = self._db.Get(key)
        data += d
        data.append(0)  # TODO set data
        data.append(0)  # TODO set data
        return decode_chunk(bytes(data))
