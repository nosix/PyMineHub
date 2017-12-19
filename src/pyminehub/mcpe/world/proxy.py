from collections import deque
from pkgutil import get_data
from typing import Optional, Deque

from pyminehub import config
from pyminehub.mcpe.const import GameMode, Difficulty
from pyminehub.mcpe.world.action import ActionType, Action
from pyminehub.mcpe.world.event import EventType, Event, event_factory

_CRAFGING_DATA_RECIPE = get_data(__package__, 'crafting-data-recipe.dat')


class WorldProxy:

    def __init__(self) -> None:
        self._event_queue = deque()  # type: Deque[Event]
        self._seed = config.get_value(config.ConfigKey.SEED)
        self._name = config.get_value(config.ConfigKey.WORLD_NAME)
        self._game_mode = GameMode.SURVIVAL
        self._difficulty = Difficulty.NORMAL
        self._rain_level = 0.0
        self._lightning_level = 0.0

    def perform(self, action: Action) -> None:
        if ActionType(action.id) == ActionType.LOGIN_PLAYER:
            self._event_queue.append(event_factory.create(EventType.PLAYER_LOGGED_IN, action.player_id))
            return
        if ActionType(action.id) == ActionType.UNKNOWN1:
            self._event_queue.append(event_factory.create(EventType.UNKNOWN1, action.player_id))

    def next_event(self) -> Optional[Event]:
        try:
            return self._event_queue.popleft()
        except IndexError:
            return None

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

    @staticmethod
    def get_recipe() -> bytes:
        return _CRAFGING_DATA_RECIPE
