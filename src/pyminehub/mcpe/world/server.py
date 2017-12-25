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
            PlayerPermission.MEMBER,
            (
                Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:health'),
                Attribute(0.0, 2048.0, 16.0, 16.0, 'minecraft:follow_range'),
                Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:knockback_resistance'),
                Attribute(0.0, 3.4028234663852886e+38, 0.10000000149011612, 0.10000000149011612, 'minecraft:movement'),
                Attribute(0.0, 3.4028234663852886e+38, 1.0, 1.0, 'minecraft:attack_damage'),
                Attribute(0.0, 3.4028234663852886e+38, 0.0, 0.0, 'minecraft:absorption'),
                Attribute(0.0, 20.0, 10.0, 20.0, 'minecraft:player.saturation'),
                Attribute(0.0, 5.0, 0.8000399470329285, 0.0, 'minecraft:player.exhaustion'),
                Attribute(0.0, 20.0, 20.0, 20.0, 'minecraft:player.hunger'),
                Attribute(0.0, 24791.0, 0.0, 0.0, 'minecraft:player.level'),
                Attribute(0.0, 1.0, 0.0, 0.0, 'minecraft:player.experience')
            )
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

    def get_adventure_settings(self) -> AdventureSettings:
        return AdventureSettings(32, 4294967295)


def run() -> WorldProxy:
    return _World()
