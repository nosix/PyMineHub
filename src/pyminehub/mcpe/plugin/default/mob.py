import random
from typing import Tuple

from pyminehub.mcpe.const import EntityType
from pyminehub.mcpe.plugin.mob import *

__all__ = [
    'DefaultMobProcessor'
]


_SPAWN_RATIO = 0.1
_SPAWN_MAX = 10


class DefaultMobProcessor(MobProcessorPlugin):

    def __init__(self) -> None:
        self._player_spawn_position = None
        self._mob_position = None

    def update(self, player_info: Tuple[PlayerInfo, ...], mob_info: Tuple[MobInfo, ...]) -> Tuple[MobAction, ...]:
        actions = []
        if len(mob_info) < _SPAWN_MAX and len(player_info) > 0 and random.random() < _SPAWN_RATIO:
            entity_type = EntityType.CHICKEN
            player = random.choice(player_info)
            position = player.position.copy(
                x=player.position.x + (random.random() - 0.5) * 10,
                z=player.position.z + (random.random() - 0.5) * 10,
            )
            actions.append(MobSpawn(len(mob_info), entity_type, entity_type.name, position, 0.0, 0.0, False))

        for mob in mob_info:
            position = mob.position.copy(
                x=mob.position.x + random.random() - 0.5,
                z=mob.position.z + random.random() - 0.5
            )
            actions.append(MobMove(mob.mob_id, position, random.randint(0, 90), random.randint(0, 360)))

        return tuple(actions)
