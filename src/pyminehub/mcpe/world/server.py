import asyncio
from collections import deque
from logging import getLogger

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.chunk import encode_chunk
from pyminehub.mcpe.inventory import create_inventory
from pyminehub.mcpe.world.action import Action, ActionType
from pyminehub.mcpe.world.database import DataBase
from pyminehub.mcpe.world.event import *
from pyminehub.mcpe.world.generator import SpaceGenerator
from pyminehub.mcpe.world.proxy import WorldProxy
from pyminehub.mcpe.world.space import Space
from pyminehub.value import LogString

_logger = getLogger(__name__)


class _World(WorldProxy):

    def __init__(self, loop: asyncio.AbstractEventLoop, generator: SpaceGenerator, db: DataBase) -> None:
        self._loop = loop
        self._space = Space(generator, db)
        self._event_queue = deque()
        self._next_entity_id = 2
        loop.call_soon(self._space.init_space)

    def perform(self, action: Action) -> None:
        _logger.debug('>> %s', LogString(action))
        self._loop.call_soon(
            getattr(self, '_process_' + ActionType(action.id).name.lower()), action)

    def next_event(self) -> Optional[Event]:
        try:
            event = self._event_queue.popleft()
            _logger.debug('<< %s', LogString(event))
            return event
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

    def get_time(self) -> int:
        return 4800

    def get_adventure_settings(self) -> AdventureSettings:
        return AdventureSettings(32, 4294967295)

    # local methods

    def _notify_event(self, event: Event) -> None:
        self._event_queue.append(event)

    # action handling methods

    def _process_login_player(self, action: Action) -> None:
        position = Vector3(256.0, 57.625, 256.0)
        height = self._space.get_height(position)
        if position.y < height + 1:
            position = position.copy(y=height + 1)
        # TODO keep player
        entity_id = self._next_entity_id
        self._next_entity_id += 1
        self._notify_event(event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            action.player_id,
            entity_id,
            entity_id,
            GameMode.SURVIVAL,
            position,
            0.0,
            358.0,
            Vector3(512, 56, 512),
            Vector3(0, 0, 0),
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
            ),
            EntityMetaDataFlagValue.create(
                always_show_nametag=True,
                immobile=True,
                swimmer=True,
                affected_by_gravity=True,
                fire_immune=True
            )
        ))

    def _process_unknown1(self, action: Action) -> None:
        self._notify_event(event_factory.create(
            EventType.UNKNOWN1,
            action.player_id,
            (
                create_inventory(WindowType.INVENTORY),
                create_inventory(WindowType.ARMOR),
                create_inventory(WindowType.CREATIVE)
            )
        ))

    def _process_unknown2(self, action: Action) -> None:
        self._notify_event(event_factory.create(
            EventType.UNKNOWN2,
            action.player_id,
            Slot(id=0, aux_value=None, nbt=None, place_on=None, destroy=None),
            0,
            0
        ))

    def _process_request_chunk(self, action: Action) -> None:
        for request in action.positions:
            chunk = self._space.get_chunk(request)
            self._event_queue.append(event_factory.create(
                EventType.FULL_CHUNK_LOADED, request.position, encode_chunk(chunk)))


def run(loop: asyncio.AbstractEventLoop) -> WorldProxy:
    from pyminehub.mcpe.world.database import DataBase
    from pyminehub.mcpe.world.generator import BatchSpaceGenerator
    db = DataBase()
    world = _World(loop, BatchSpaceGenerator(), db)
    return world
