import asyncio
from logging import getLogger

from pyminehub.config import ConfigKey, get_value
from pyminehub.mcpe.action import Action, ActionType
from pyminehub.mcpe.attribute import create_attribute
from pyminehub.mcpe.chunk import encode_chunk
from pyminehub.mcpe.event import *
from pyminehub.mcpe.world.database import DataBase
from pyminehub.mcpe.world.entity import EntityPool
from pyminehub.mcpe.world.generator import SpaceGenerator
from pyminehub.mcpe.world.proxy import WorldProxy
from pyminehub.mcpe.world.space import Space
from pyminehub.value import LogString

_logger = getLogger(__name__)


class _World(WorldProxy):

    def __init__(self, loop: asyncio.AbstractEventLoop, generator: SpaceGenerator, db: DataBase) -> None:
        self._loop = loop
        self._space = Space(generator, db)
        self._entity = EntityPool()
        self._event_queue = asyncio.Queue()
        loop.call_soon(self._space.init_space)

    def perform(self, action: Action) -> None:
        _logger.debug('>> %s', LogString(action))
        self._loop.call_soon(
            getattr(self, '_process_' + ActionType(action.id).name.lower()), action)

    async def next_event(self) -> Optional[Event]:
        event = await self._event_queue.get()
        _logger.debug('<< %s', LogString(event))
        return event

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
        self._event_queue.put_nowait(event)

    # action handling methods

    def _process_login_player(self, action: Action) -> None:
        entity_runtime_id = self._entity.load_player(action.player_id)
        entity = self._entity.get_player(entity_runtime_id)
        height = self._space.get_height(entity.spawn_position)
        entity.spawn(height)

        self._notify_event(event_factory.create(
            EventType.PLAYER_LOGGED_IN,
            entity.player_id,
            entity.entity_unique_id,
            entity_runtime_id,
            GameMode.SURVIVAL,
            entity.position,
            entity.pitch,
            entity.yaw,
            entity.sapwn_position,
            Vector3(0, 0, 0),
            PlayerPermission.MEMBER,
            (
                create_attribute(AttributeType.HEALTH, entity.health),
                create_attribute(AttributeType.FOLLOW_RANGE, 16.0),
                create_attribute(AttributeType.KNOCKBACK_RESISTANCE, 0.0),
                create_attribute(AttributeType.MOVEMENT, 0.10000000149011612),
                create_attribute(AttributeType.ATTACK_DAMAGE, 1.0),
                create_attribute(AttributeType.ABSORPTION, 0.0),
                create_attribute(AttributeType.PLAYER_SATURATION, 10.0),
                create_attribute(AttributeType.PLAYER_EXHAUSTION, 0.8000399470329285),
                create_attribute(AttributeType.PLAYER_HUNGER, entity.hunger),
                create_attribute(AttributeType.PLAYER_LEVEL, 0.0),
                create_attribute(AttributeType.PLAYER_EXPERIENCE, 0.0)
            ),
            EntityMetaDataFlagValue.create(
                always_show_nametag=True,
                immobile=True,
                swimmer=True,
                affected_by_gravity=True,
                fire_immune=True
            )
        ))
        self._notify_event(event_factory.create(
            EventType.INVENTORY_LOADED,
            entity.player_id,
            (
                entity.get_inventory(WindowType.INVENTORY),
                entity.get_inventory(WindowType.ARMOR),
                entity.get_inventory(WindowType.CREATIVE)
            )
        ))
        self._notify_event(event_factory.create(
            EventType.SLOT_INITIALIZED,
            entity.player_id,
            Slot(id=0, aux_value=None, nbt=None, place_on=None, destroy=None),
            0,
            0
        ))

    def _process_request_chunk(self, action: Action) -> None:
        for request in action.positions:
            chunk = self._space.get_chunk(request)
            self._notify_event(event_factory.create(
                EventType.FULL_CHUNK_LOADED, request.position, encode_chunk(chunk)))

    def _process_move_player(self, action: Action) -> None:
        self._notify_event(event_factory.create(
            EventType.PLAYER_MOVED,
            action.entity_runtime_id,
            action.position,
            action.pitch,
            action.yaw,
            action.head_yaw,
            action.mode,
            action.on_ground,
            action.riding_eid
        ))

    def _process_use_item(self, action: Action) -> None:
        pass  # TODO implement


def run(loop: asyncio.AbstractEventLoop) -> WorldProxy:
    from pyminehub.mcpe.world.database import DataBase
    from pyminehub.mcpe.world.generator import BatchSpaceGenerator
    db = DataBase()
    world = _World(loop, BatchSpaceGenerator(), db)
    return world
