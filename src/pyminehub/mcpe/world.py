from pyminehub import config
from pyminehub.mcpe.const import GameMode, Difficulty


class WorldProxy:

    def __init__(self):
        self._seed = config.get_value(config.ConfigKey.SEED)
        self._name = config.get_value(config.ConfigKey.WORLD_NAME)
        self._game_mode = GameMode.SURVIVAL
        self._difficulty = Difficulty.NORMAL
        self._rain_level = 0.0
        self._lightning_level = 0.0

    def get_seed(self) -> int:
        return self._seed

    def get_game_mode(self) -> GameMode:
        return self._game_mode

    def get_difficulty(self) -> Difficulty:
        return self._difficulty

    def get_rain_level(self) -> float:
        return self._rain_level

    def get_lightning_level(self) -> float:
        return self._lightning_level

    def get_world_name(self) -> str:
        return self._name
