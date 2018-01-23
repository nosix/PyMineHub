from pyminehub.mcpe.const import GameMode
from pyminehub.mcpe.value import PlayerID


__all__ = [
    'PlayerConfigPlugin'
]


class PlayerConfigPlugin:

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        raise NotImplementedError()
