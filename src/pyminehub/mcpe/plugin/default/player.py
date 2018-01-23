from pyminehub.mcpe.const import GameMode
from pyminehub.mcpe.plugin.player import PlayerConfigPlugin
from pyminehub.mcpe.value import PlayerID

__all__ = [
    'DefaultPlayerConfig'
]


class DefaultPlayerConfig(PlayerConfigPlugin):

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        return world_game_mode
