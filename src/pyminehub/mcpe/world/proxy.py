from pkgutil import get_data
from typing import Optional

from pyminehub.mcpe.const import GameMode, Difficulty
from pyminehub.mcpe.world.action import Action
from pyminehub.mcpe.world.event import Event

_CRAFGING_DATA_RECIPE = get_data(__package__, 'crafting-data-recipe.dat')


class WorldProxy:

    @staticmethod
    def get_recipe() -> bytes:
        return _CRAFGING_DATA_RECIPE

    def perform(self, action: Action) -> None:
        raise NotImplementedError()

    def next_event(self) -> Optional[Event]:
        raise NotImplementedError()

    def get_seed(self) -> int:
        raise NotImplementedError()

    def get_game_mode(self) -> GameMode:
        raise NotImplementedError()

    def get_difficulty(self) -> Difficulty:
        raise NotImplementedError()

    def get_rain_level(self) -> float:
        raise NotImplementedError()

    def get_lightning_level(self) -> float:
        raise NotImplementedError()

    def get_world_name(self) -> str:
        raise NotImplementedError()

    def get_time(self) -> int:
        raise NotImplementedError()
