from typing import Optional

from pyminehub.mcpe.action import Action
from pyminehub.mcpe.const import GameMode, Difficulty
from pyminehub.mcpe.event import Event
from pyminehub.mcpe.resource import CRAFTING_DATA_RECIPE
from pyminehub.mcpe.value import AdventureSettings


class WorldProxy:

    @staticmethod
    def get_recipe() -> bytes:
        return CRAFTING_DATA_RECIPE

    def terminate(self) -> None:
        raise NotImplementedError()

    def perform(self, action: Action) -> None:
        raise NotImplementedError()

    async def next_event(self) -> Optional[Event]:
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

    def get_adventure_settings(self) -> AdventureSettings:
        raise NotImplementedError()
