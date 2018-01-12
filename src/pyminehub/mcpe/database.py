import pickle
import sqlite3

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.chunk import Chunk, encode_chunk, decode_chunk
from pyminehub.mcpe.value import *

_PICKLE_PROTOCOL = 4


class DataBase:

    def delete_all(self) -> None:
        raise NotImplementedError()

    def save_chunk(self, position: ChunkPosition, chunk: Chunk, insert_only=False) -> None:
        raise NotImplementedError()

    def load_chunk(self, position: ChunkPosition) -> Optional[Chunk]:
        raise NotImplementedError()

    def count_chunk(self) -> int:
        raise NotImplementedError()

    def save_player(self, player_id: str, player: PlayerState, insert_only=False) -> None:
        raise NotImplementedError()

    def load_player(self, player_id: str) -> Optional[PlayerState]:
        raise NotImplementedError()


class _DataBaseImpl(DataBase):

    def __init__(self, name: str) -> None:
        self._connection = sqlite3.connect(name + '.db')
        self._create_table()

    def _create_table(self) -> None:
        with self._connection:
            self._connection.execute(
                'CREATE TABLE IF NOT EXISTS chunk(x INTEGER, z INTEGER, data BLOB, PRIMARY KEY(x, z))')
            self._connection.execute(
                'CREATE TABLE IF NOT EXISTS player(player_id TEXT, data BLOB, PRIMARY KEY(player_id))')

    def delete_all(self) -> None:
        with self._connection:
            self._connection.execute('DELETE FROM chunk')
            self._connection.execute('DELETE FROM player')

    def save_chunk(self, position: ChunkPosition, chunk: Chunk, insert_only=False) -> None:
        encoded_chunk = encode_chunk(chunk)
        param = (encoded_chunk, position.x, position.z)
        with self._connection:
            if not insert_only:
                self._connection.execute(
                    'UPDATE chunk SET data=? WHERE x=? AND z=?', param)
            self._connection.execute(
                'INSERT OR IGNORE INTO chunk(data,x,z) VALUES(?,?,?)', param)

    def load_chunk(self, position: ChunkPosition) -> Optional[Chunk]:
        param = (position.x, position.z)
        row = self._connection.execute('SELECT data FROM chunk WHERE x=? AND z=?', param).fetchone()
        return decode_chunk(row[0]) if row else None

    def count_chunk(self) -> int:
        row = self._connection.execute('SELECT count(*) FROM chunk').fetchone()
        return row[0] if row else 0

    def save_player(self, player_id: str, player: PlayerState, insert_only=False) -> None:
        param = (pickle.dumps(player, protocol=_PICKLE_PROTOCOL), player_id)
        with self._connection:
            if not insert_only:
                self._connection.execute(
                    'UPDATE player SET data=? WHERE player_id=?', param)
            self._connection.execute(
                'INSERT OR IGNORE INTO player(data,player_id) VALUES(?,?)', param)

    def load_player(self, player_id: str) -> Optional[PlayerState]:
        param = (player_id, )
        row = self._connection.execute('SELECT data FROM player WHERE player_id=?', param).fetchone()
        return pickle.loads(row[0]) if row else None


def create_database() -> DataBase:
    world_name = get_value(ConfigKey.WORLD_NAME)
    name = world_name.replace(' ', '_')
    seed = get_value(ConfigKey.SEED)
    suffix = ('p' if seed >= 0 else 'n') + str(seed)
    db_name = '{}-{}'.format(name, suffix)
    return _DataBaseImpl(db_name)
