from pyminehub.mcpe.plugin.mob import *


class DefaultMobProcessor(MobProcessor):

    def __init__(self) -> None:
        self._mob_exists = False
        self._player_spawn_position = None

    def update(self, player_info: Tuple[PlayerInfo, ...], chunk_info: Tuple[ChunkInfo, ...]) -> Tuple[MobAction, ...]:
        # TODO move to another module
        if self._player_spawn_position is None:
            if len(player_info) > 0:
                self._player_spawn_position = player_info[0].position
                return tuple()
        if not self._mob_exists:
            if len(player_info) > 0 and player_info[0].position.distance(self._player_spawn_position) > 5:
                self._mob_exists = True
                return MobSpawn(0, EntityType.CHICKEN, 'PiyoPiyo', self._player_spawn_position, 0.0, 0.0, False),
        return tuple()
