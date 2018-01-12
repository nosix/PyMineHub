from pyminehub.mcpe.plugin.player import *


class DefaultPlayerConfig(PlayerConfig):

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        return world_game_mode
