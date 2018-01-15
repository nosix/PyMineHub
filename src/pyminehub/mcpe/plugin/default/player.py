from pyminehub.mcpe.plugin.player import *


class DefaultPlayerConfig(PlayerConfigPlugin):

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        return world_game_mode
