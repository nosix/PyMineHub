from collections import deque
from pkgutil import get_data

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.world.action import Action, ActionType
from pyminehub.mcpe.world.event import *
from pyminehub.mcpe.world.proxy import WorldProxy


class _World(WorldProxy):

    def __init__(self) -> None:
        self._event_queue = deque()
        self._chunk_data = get_data(__package__, 'chunk_data.dat')  # TODO remove this

    def perform(self, action: Action) -> None:
        getattr(self, '_process_' + ActionType(action.id).name.lower())(action)

    def next_event(self) -> Optional[Event]:
        try:
            return self._event_queue.popleft()
        except IndexError:
            return None

    def get_seed(self) -> int:
        return get_value(ConfigKey.SEED)

    def get_game_mode(self) -> GameMode:
        return GameMode[get_value(ConfigKey.GAME_MODE)]

    def get_difficulty(self) -> Difficulty:
        return Difficulty[get_value(ConfigKey.DIFFICULTY)]

    def get_rain_level(self) -> float:
        return get_value(ConfigKey.RAIN_LEVEL)

    def get_lightning_level(self) -> float:
        return get_value(ConfigKey.LIGHTNING_LEVEL)

    def get_world_name(self) -> str:
        return get_value(ConfigKey.WORLD_NAME)

    # local methods

    def _notify_event(self, event: Event) -> None:
        self._event_queue.append(event)

    # action handling methods

    def _process_login_player(self, action: Action) -> None:
        # TODO keep player
        self._notify_event(event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            action.player_id,
            1,
            1,
            GameMode.SURVIVAL,
            Vector3(256.0, 57.625, 256.0),
            0.0,
            358.0,
            Vector3(512, 56, 512),
            PlayerPermission.MEMBER
        ))

    def _process_unknown1(self, action: Action) -> None:
        self._notify_event(event_factory.create(EventType.UNKNOWN1, action.player_id))

    def _process_unknown2(self, action: Action) -> None:
        self._notify_event(event_factory.create(EventType.UNKNOWN2, action.player_id))

    def _process_request_chunk(self, action: Action) -> None:
        for position in action.positions:
            self._event_queue.append(event_factory.create(
                EventType.FULL_CHUNK_LOADED, position.position, self._chunk_data))

    def get_time(self) -> int:
        return 4800


def run() -> WorldProxy:
    return _World()
