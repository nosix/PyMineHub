from typing import NamedTuple as _NamedTuple, Optional, Tuple, Union

from pyminehub.mcpe.chunk import Chunk
from pyminehub.mcpe.const import EntityType
from pyminehub.mcpe.geometry import Vector3

__all__ = [
    'MobID',
    'PlayerID',
    'MobSpawn',
    'MobMove',
    'MobAction',
    'PlayerInfo',
    'MobInfo',
    'MobProcessorPlugin'
]


MobID = int
PlayerID = int

MobSpawn = _NamedTuple('MobSpawn', [
    ('mob_id', MobID),
    ('type', EntityType),
    ('name', Optional[str]),
    ('position', Vector3[float]),
    ('pitch', float),
    ('yaw', float),
    ('monitor_nearby_chunks', bool)
])

MobMove = _NamedTuple('MobMove', [
    ('mob_id', MobID),
    ('position', Vector3[float]),
    ('pitch', float),
    ('yaw', float),
])

PlayerInfo = _NamedTuple('PlayerInfo', [
    ('player_id', PlayerID),
    ('position', Vector3[float]),
    ('pitch', float),
    ('yaw', float),
    ('head_yaw', float)
])

MobInfo = _NamedTuple('MobInfo', [
    ('mob_id', MobID),
    ('position', Vector3[float]),
    ('nearby_chunks', Tuple[Chunk, ...])
])

MobAction = Union[MobSpawn, MobMove]


class MobProcessorPlugin:

    def update(self, player_info: Tuple[PlayerInfo, ...], mob_info: Tuple[MobInfo, ...]) -> Tuple[MobAction, ...]:
        raise NotImplementedError()
