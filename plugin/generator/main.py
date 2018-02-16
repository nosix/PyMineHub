import leveldb
from enum import Enum
from pathlib import Path

from pyminehub.binutil.composite import CompositeCodec
from pyminehub.binutil.converter import Endian, IntData, EnumData
from pyminehub.binutil.instance import BYTE_DATA
from pyminehub.mcpe.chunk import Chunk, decode_chunk, create_empty_chunk, foreach_xz
from pyminehub.mcpe.const import BlockType, BiomeType
from pyminehub.mcpe.geometry import Vector3, ChunkPosition
from pyminehub.mcpe.plugin.generator import ChunkGeneratorPlugin
from pyminehub.mcpe.value import Block


class _Tag(Enum):
    LEGACY_TERRAIN = 48
    BLOCK_ENTITY = 49
    ENTITY = 50
    VERSION = 118


class ChunkGeneratorPluginImpl(ChunkGeneratorPlugin):

    _key_codec = CompositeCodec([
        IntData(endian=Endian.LITTLE),
        IntData(endian=Endian.LITTLE),
        EnumData(BYTE_DATA, _Tag)
    ])

    _VERSION_2 = bytes([2])

    def __init__(self) -> None:
        db_root = Path(Path(__file__).parent, 'db')
        self._db = leveldb.LevelDB(str(db_root))
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
                key = self._key_codec.encode(position.x, position.z, _Tag.LEGACY_TERRAIN)
                data = self._db.Get(key)
                return decode_chunk(data, is_legacy=True)
        except leveldb.LevelDBError:
            pass
        return self._default_chunk
