import sqlite3

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.chunk import Chunk, encode_chunk, decode_chunk
from pyminehub.mcpe.geometry import ChunkPosition


class DataBase:

    def __init__(self) -> None:
        world_name = get_value(ConfigKey.WORLD_NAME)
        name = world_name.replace(' ', '_')
        seed = get_value(ConfigKey.SEED)
        suffix = ('p' if seed >= 0 else 'n') + str(seed)
        self._connection = sqlite3.connect('{}-{}.db'.format(name, suffix))
        self._create_table()

    def _create_table(self) -> None:
        with self._connection:
            self._connection.execute(
                'CREATE TABLE IF NOT EXISTS chunk(x INTEGER, z INTEGER, data BLOB, PRIMARY KEY(x, z))')

    def save_chunk(self, position: ChunkPosition, chunk: Chunk, insert_only=False):
        encodec_chunk = encode_chunk(chunk)
        param = (encodec_chunk, position.x, position.z)
        with self._connection:
            if not insert_only:
                self._connection.execute(
                    'UPDATE chunk SET data=? WHERE x=? AND z=?', param)
            self._connection.execute(
                'INSERT OR IGNORE INTO chunk(data,x,z) VALUES(?,?,?)', param)

    def load_chunk(self, position: ChunkPosition) -> Chunk:
        param = (position.x, position.z)
        row = self._connection.execute('SELECT data FROM chunk WHERE x=? AND z=?', param).fetchone()
        chunk = decode_chunk(row[0]) if row else None
        return chunk

    def count_chunk(self) -> int:
        row = self._connection.execute('SELECT count(*) FROM chunk').fetchone()
        return row if row else 0
