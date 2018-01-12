from pyminehub.mcpe.const import GameMode
from pyminehub.mcpe.value import PlayerID


class PlayerConfig:

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        raise NotImplementedError()
