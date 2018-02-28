from pyminehub.mcpe.const import GameMode
from pyminehub.mcpe.value import PlayerID


__all__ = [
    'PlayerConfigPlugin'
]


class PlayerConfigPlugin:

    def get_game_mode(self, world_game_mode: GameMode, player_id: PlayerID) -> GameMode:
        """Return game mode for specified player.

        :param world_game_mode: SURVIVAL or CREATIVE (currently ADVENTURE is not supported)
        :param player_id: designating player
        :return: game mode (SURVIVAL or CREATIVE)
        """
        raise NotImplementedError()
