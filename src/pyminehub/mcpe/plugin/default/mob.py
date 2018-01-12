import random

from pyminehub.mcpe.plugin.mob import *


class DefaultMobProcessor(MobProcessor):

    def __init__(self) -> None:
        self._player_spawn_position = None
        self._mob_position = None

    def update(self, player_info: Tuple[PlayerInfo, ...], chunk_info: Tuple[ChunkInfo, ...]) -> Tuple[MobAction, ...]:
        # TODO move to another module
        if self._player_spawn_position is None:
            if len(player_info) > 0:
                self._player_spawn_position = player_info[0].position
                return tuple()
        if self._mob_position is None:
            if len(player_info) > 0 and player_info[0].position.distance(self._player_spawn_position) > 5:
                self._mob_position = self._player_spawn_position
                return MobSpawn(0, EntityType.CHICKEN, 'PiyoPiyo', self._player_spawn_position, 0.0, 0.0, False),
            else:
                return tuple()
        self._mob_position = self._mob_position.copy(
            x=self._mob_position.x + random.random() - 0.5,
            z=self._mob_position.z + random.random() - 0.5
        )
        return MobMove(0, self._mob_position, random.randint(0, 90), random.randint(0, 360)),
